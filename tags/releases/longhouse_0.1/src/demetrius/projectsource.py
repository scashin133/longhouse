#!/usr/bin/env python
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


from ezt import ezt

from common import ezt_google
from common import post

from demetrius import constants
from demetrius import helpers
from demetrius import pageclasses
from demetrius import permissions


class ProjectSource(pageclasses.DemetriusPage):
  """This is the page accessed from the "source" tab."""

  _PAGE_TEMPLATE = 'demetrius/project-source-page.ezt' # TODO: make this template
  _MAIN_TAB_MODE = constants.MAIN_TAB_SOURCE

  def AssertBasePermission(self, req_info):
    pageclasses.DemetriusPage.AssertBasePermission(self, req_info)
    # TODO: i18n error messages
    if not req_info.demetrius_perms.Check(permissions.VIEW_PROJECT):
      raise permissions.PermissionException(
        "You are not allowed to view this project's source")

  def GatherPageData(self, request, req_info):
    """Build up a dictionary of data values to use when rendering the page."""
    page_data = {
      'errors': req_info.errors or ezt_google.EZTError(),
      'show_help': ezt.boolean(req_info.user_pb and
                               req_info.user_pb.keep_wiki_help_open()),
      'analytics_account': req_info.GetParam(
                             'analytics_account',
                             req_info.project.analytics_account()),
      }

    meta = helpers.BuildProjectMeta(req_info.project, self.demetrius_persist)
    links = helpers.BuildProjectLinks(req_info.project)
    
    page_data.update(meta)
    page_data.update(links)

    post.URLCommandAttacksEncode(page_data, req_info.logged_in_user_id)
    return page_data


