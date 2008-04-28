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

"""Page and form handlers for issue tracker configuration.

This class implements the "issue tracker" subtab under the "Administer" tab.
It is a single page with a multi-section form that allows a project owner to
edit:
 + The lists of well-known open and closed issue statuses
 + The list of well-known issue labels
 + A set of exclusive label prefixes.
 + The prompts presented to users when they enter a new issue.
"""

import re
import time

from common import http
from common import post

from framework import artifactlist
import framework.helpers
import framework.constants

import demetrius.constants
from demetrius import permissions

import dit.helpers
import dit.pageclasses
import dit.constants


class ProjectAdminIssues(dit.pageclasses.DITPage):
  """A page and form allowing project owners to configure the issue tracker."""

  _PAGE_TEMPLATE = 'dit/issue-admin-page.ezt'
  _MAIN_TAB_MODE = demetrius.constants.MAIN_TAB_ADMIN

  def AssertBasePermission(self, req_info):
    """Check whether the user has any permission to visit this page.

    Args:
      req_info: commonly used info parsed from the request.
    """

    dit.pageclasses.DITPage.AssertBasePermission(self, req_info)

    if not req_info.demetrius_perms.Check(permissions.EDIT_PROJECT):
      raise permissions.PermissionException(
        'You are not allowed to administer this project')

  def GatherPageData(self, request, req_info):
    """Build up a dictionary of data values to use when rendering the page.

    Args:
      request: the HTTP request being processed.
      req_info: commonly used info parsed from the request.

    Returns: dict of values used by EZT for rendering almost all DIT pages.
    """

    page_data = {
      'admin_tab_mode': demetrius.constants.ADMIN_TAB_ISSUES,
      }

    config = dit.helpers.BuildProjectIssuesConfig(req_info.project,
                                                 self.dit_persist)
    page_data.update(config)
    post.URLCommandAttacksEncode(page_data, req_info.logged_in_user_id)

    return page_data

  def ProcessForm(self, request, req_info):
    """Validate and store the contents of the issues tracker admin page.

    Args:
      request: the HTTP request being processed.
      req_info: commonly used info parsed from the request.
    """

    post_data = post.ProcessPOSTBody(
        request, framework.constants.MAX_POST_BODY_SIZE)
    if post_data is None:
      # An error occurred and the response was generated. We're done.
      raise framework.helpers.AlreadySentResponse()

    self.demetrius_persist.LockProject(req_info.project_name)
    try:
      self.ProcessAdminIssuesForm(post_data, req_info)
    finally:
      self.demetrius_persist.UnlockProject(req_info.project_name)

    url = framework.helpers.FormatAbsoluteURL(
      req_info, dit.constants.ADMIN_ISSUES_PAGE_URL, request,
      saved=1, ts=int(time.time()))
    http.SendRedirect(url, request)

  def ProcessAdminIssuesForm(self, post_data, req_info):
    """Process the project issues section of the admin page.

    Args:
      post_data: HTML form data for the HTTP request being processed.
      req_info: commonly used info parsed from the request.
    """

    wks_open_text = ''
    if 'predefinedopen' in post_data:
      wks_open_text = post_data['predefinedopen'][0]
    wks_open_matches = framework.constants.IDENTIFIER_DOCSTRING_RE.findall(
      wks_open_text)
    wks_open_tuples = [
      (post.CanonicalizeLabel(status), docstring.strip(), True)
      for status, docstring in wks_open_matches]

    wks_closed_text = ''
    if 'predefinedclosed' in post_data:
      wks_closed_text = post_data['predefinedclosed'][0]
    wks_closed_matches = framework.constants.IDENTIFIER_DOCSTRING_RE.findall(
      wks_closed_text)
    wks_closed_tuples = [
      (post.CanonicalizeLabel(status), docstring.strip(), False)
      for status, docstring in wks_closed_matches]

    wkl_text = ''
    if 'predefinedlabels' in post_data:
      wkl_text = post_data['predefinedlabels'][0]
    wkl_matches = framework.constants.IDENTIFIER_DOCSTRING_RE.findall(wkl_text)
    wkl_tuples = [
      (post.CanonicalizeLabel(label), docstring.strip())
      for label, docstring in wkl_matches]

    excl_prefix_text = ''
    if 'excl_prefixes' in post_data:
      excl_prefix_text = post_data['excl_prefixes'][0]
    excl_prefixes = framework.constants.IDENTIFIER_RE.findall(excl_prefix_text)

    wkp_tuples = []
    while ('promptname%s' % len(wkp_tuples)) in post_data:
      prompt_name = post_data['promptname%s' % len(wkp_tuples)][0]
      prompt_text = ''
      if 'prompt%s' % len(wkp_tuples) in post_data:
        prompt_text = post_data['prompt%s' % len(wkp_tuples)][0]
      # undo the effect of JSEscape(), needed when prompt was not edited.
      prompt_text = prompt_text.replace(r'\n', '\n')
      wkp_tuples.append((prompt_name, prompt_text))

    # For now, just hard code the canned-queries
    # TODO: allow canned query customization.
    canned_queries = dit.constants.DEFAULT_CANNED_QUERIES

    list_prefs = artifactlist.ParseListPreferences(
      post_data, dit.constants.DEFAULT_COL_SPEC)

    self.dit_persist.UpdateConfigInLockedProject(
      req_info.project, self.conn_pool, canned_queries=canned_queries,
      well_known_statuses=wks_open_tuples + wks_closed_tuples,
      well_known_labels=wkl_tuples, excl_label_prefixes=excl_prefixes,
      well_known_prompts=wkp_tuples, list_prefs=list_prefs)
