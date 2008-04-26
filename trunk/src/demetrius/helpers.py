#!/usr/bin/python2.4
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Helper functions and classes used by the Demetrius pages.

Each function garthers data for one section of a Demetrius page.  The functions
place the data in a context, which is passed to EZT to output the HTML.
"""

import sys
import urllib
import threading

from ezt import ezt

from twisted.python import log

from common import post
from common import http
from common import ezt_google

import framework.helpers

from bo import demetrius_pb
from demetrius import licenses
from demetrius import constants


def BuildProjectMeta(project, demetrius_persist):
  """Gather data for the metadata section of a project page."""

  label_names = project.labels_list()

  meta_data = {
    'project_labels': [post.CanonicalizeLabel(label) for label in label_names
                       if label.strip()],  # Skip blank labels.
    'project_license': LicenseProxy(project),
    }

  # TODO: convert to a sequence rather than individual vars.
  for i in xrange(15):
    if i < len(label_names):
      meta_data['label%s' % (i + 1)] = label_names[i]
    else:
      meta_data['label%s' % (i + 1)] = ''

  return meta_data


def BuildProjectMembers(project, demetrius_persist, max_members_to_lookup=None):
  """Gather data for the members section of a project page.

  Args:
    project: Project PB of current project.
    conn_pool: connection to AuthSub servers.
    max_members_to_lookup: integer limit on number of members to look up.
      Project with more than the max will not show any members, just owners.
      Defaults to showing any number of members, even if it will be
      slow to retrieve that data.

  Returns: a dictionary suitable for use with EZT.
  """
  display_members = True
  if max_members_to_lookup is not None:
    display_members = len(project.member_ids_list()) <= max_members_to_lookup

  # First, get all needed info on all users in one batch of requests.
  all_user_ids = project.owner_ids_list()[:]
  if display_members:
    all_user_ids.extend(project.member_ids_list())
  #cuis_by_id = conn_pool.GetClientUserInfoBatch(all_user_ids)

  # Second, group the user proxys by role for display.
  owner_proxies = [framework.helpers.UserIDProxy(
                     user_id, demetrius_persist)
                   for user_id in project.owner_ids_list()]
  member_proxies = []
  if display_members:
    member_proxies = [framework.helpers.UserIDProxy(
                        user_id, demetrius_persist)
                      for user_id in project.member_ids_list()]
  return {
    'owners': owner_proxies,
    'members': member_proxies,
    'member_count': len(project.member_ids_list()),
    'display_members': ezt.boolean(display_members),
    }


def BuildProjectLinks(project, urls=None, groups=None, blogs=None):
  """Gather data for the links section of a project page.

  Link data is retrieved from the supplied project except when data
  is supplied to override the project data. When any of the named
  arguments are defined, data will be loaded from them rather than the
  project.

  Args:
    project: a project desription (demetrius_pb.Project)
    urls: a list of (label, url). When specified, url data will not
      be loaded from the project.
    groups: a list of (label, groupid). When specified, group data
      will not be loaded from the project.
    blogs: a list of (label, url). When specified, blog data
      will not be loaded from the project.
  """

  # We store an array index in the items so that we can correlate them
  # when the user hits submit.
  # TODO: try to find a way to handle all user input cases without index.

  result = {
    'url_links': [],
    'group_links': [],
    'blog_links': [],
  }

  url_links = urls
  if not url_links:
    url_links = [(l.label(), l.url()) for l in project.linksurl_list()]

  for i in range(len(url_links)):
    link = url_links[i]
    result['url_links'].append(ezt_google.EZTItem(
      index=i,
      label=link[0],
      direct_url=link[1],
      url = link[1],
    ))

  group_links = groups
  if not group_links:
    group_links = [(l.label(), l.group_name())
      for l in project.linksgroup_list()]

  for i in range(len(group_links)):
    (label, group_name) = group_links[i]
    if not label: label = link[1]
    result['group_links'].append(ezt_google.EZTItem(
      index=i,
      label=label,
      group_name=group_name,
    ))

  blog_links = blogs
  if not blog_links:
    blog_links = [(l.label(), l.url()) for l in project.linksblog_list()]

  for i in range(len(blog_links)):
    link = blog_links[i]
    result['blog_links'].append(ezt_google.EZTItem(
      index=i,
      label=link[0],
      direct_url=link[1],
      url = link[1],
    ))

  log.msg("Project Links: %s" % result)

  return result


def BuildLabelDefaults(req_info, label_list=None):
  """Build a dictionary of EZT data for issue or project labels.

  If this request is an internal bounce from processing an invalid
  form, echo back the labels that the user already entered.
  """
  if 'labels' in req_info.synthetic_params:
    label_list = req_info.synthetic_params['labels']
  elif req_info.GetParam('labels', None):
    label_list = req_info.GetParam('labels', '').split(',')
    label_list = [label.strip() for label in label_list]
  else:
    label_list = label_list or []

  label_data = {}
  for i in range(len(label_list)):
    label_data['label%d' % i] = label_list[i]
  for i in range(len(label_list), 15):
    label_data['label%d' % i] = ''
  return label_data


def BuildProjectAdminOptions(project, user_pb):
  """Gather data about project configuration options."""
  offered_licenses = licenses.USER_LICENSES.copy()
  if user_pb and user_pb.is_site_admin():
    offered_licenses.update(licenses.ADMIN_LICENSES)
  elif project:
    # If a project already has an admin-only license, it should appear
    # as an option even if the current user is not a site admin.
    plk = project.license_key()
    if plk not in offered_licenses:
      offered_licenses[plk] = licenses.ADMIN_LICENSES[plk]

  license_objects = [ezt_google.EZTItem(key=key, name=name, url=url)
                     for key, (name, url) in offered_licenses.items()]
  license_objects.sort(lambda a, b: cmp(a.name, b.name))

  return {
    'available_licenses': license_objects,
    }

def FilterRestrictedLabels(req_info, labels):
	# TODO actually check for a set of restricted labels
	return []

class LicenseProxy(object):
  """Provide the license information as attribute-based objects.

  These objects are more easily consumed by EZT templates.
  """

  def __init__(self, project, license_key=None):
    if license_key:
      self.key = license_key
    else:
      self.key = project.license_key()

    self.name, self.url = licenses.ALL_LICENSES[self.key]


if __name__ == '__main__':
  sys.exit('This is not meant to be run as a standalone program. Exiting.')
