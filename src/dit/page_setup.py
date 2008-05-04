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

"""This file registers urls for the Demetrius Issue Tracker pages and forms.
"""

from common import pageclasses

import framework.helpers

from dit import constants
from dit import issuelist
from dit import issueentry
from dit import issuedetail
#from dit import issuebulkedit
#from dit import issueimport
from dit import issuetips
from dit import issueadvsearch
from dit import issueattachment
from dit import issueadmin


class PageSetup(framework.helpers.AbstractPageSetup):
  """This class configures the DIT URLs."""

  # Make DIT pages only visible from Google internal IP addresses
  # until we are ready to launch.  We have launched!
  _DEFAULT_PAGE_PRIVACY = False

  def __init__(self, server, conn_pool,
               demetrius_persist, dit_persist, worktable, universal_ezt_data):
    self.server = server
    self.conn_pool = conn_pool
    self.demetrius_persist = demetrius_persist
    self.dit_persist = dit_persist
    self.worktable = worktable
    self.universal_ezt_data = universal_ezt_data.copy()

  def RegisterPages(self):
    """Register all the DIT pages, forms, and feeds with the server."""

    issue_list_page = issuelist.IssueList(
      self.conn_pool, self.demetrius_persist,
      self.dit_persist, self.universal_ezt_data)
    self._SetupProjectPage(issue_list_page.Handler,
                           constants.ISSUE_LIST_PAGE_URL)
    """
    list_redir = pageclasses.RedirectInScope(
        constants.ISSUE_LIST_PAGE_URL, 'p')
    for uri in ['/issues', '/issues/']:
      self._SetupProjectPage(list_redir.SendRedirect, uri)"""
    issue_detail_page = issuedetail.IssueDetail(
      self.conn_pool, self.demetrius_persist,
      self.dit_persist, self.universal_ezt_data, worktable=self.worktable)
    self._SetupProjectPage(issue_detail_page.Handler,
                           constants.ISSUE_DETAIL_PAGE_URL)
    self._SetupProjectForm(issue_detail_page.FormHandler,
                           constants.ISSUE_UPDATE_FORM_URL)
    
    issue_comment_del_page = issuedetail.IssueCommentDeletion(
      self.conn_pool, self.demetrius_persist,
      self.dit_persist, self.universal_ezt_data)
    self._SetupProjectForm(issue_comment_del_page.FormHandler,
                           constants.ISSUE_COMMENT_DELETION_FORM_URL)
    
    issue_entry_page = issueentry.IssueEntry(
      self.conn_pool, self.demetrius_persist,
      self.dit_persist, self.universal_ezt_data, worktable=self.worktable)
    self._SetupProjectPage(issue_entry_page.Handler,
                           constants.ISSUE_ENTRY_PAGE_URL)
    self._SetupProjectForm(issue_entry_page.FormHandler,
                           constants.ISSUE_ENTRY_FORM_URL)

    issue_options_feed = issueentry.IssueOptionsFeed(
      self.conn_pool, self.demetrius_persist,
      self.dit_persist, self.universal_ezt_data)
    self._SetupProjectPage(issue_options_feed.Handler,
                           constants.ISSUE_OPTIONS_FEED_URL)

    set_star_form = issuedetail.SetStarForm(
      self.conn_pool, self.demetrius_persist,
      self.dit_persist, self.universal_ezt_data)
    self._SetupProjectPage(set_star_form.Handler,
                           constants.ISSUE_SETSTAR_FORM_URL)
    
    issue_admin_page = issueadmin.ProjectAdminIssues(
      self.conn_pool, self.demetrius_persist,
      self.dit_persist, self.universal_ezt_data)
    self._SetupProjectPage(issue_admin_page.Handler,
                           constants.ADMIN_ISSUES_PAGE_URL)
    self._SetupProjectForm(issue_admin_page.FormHandler,
                           constants.ADMIN_ISSUES_FORM_URL)

"""
    issue_advsearch_page = issueadvsearch.IssueAdvancedSearch(
      self.conn_pool, self.demetrius_persist,
      self.dit_persist, self.universal_ezt_data)
    self._SetupProjectPage(issue_advsearch_page.Handler,
                           constants.ISSUE_ADVSEARCH_PAGE_URL)
    self._SetupProjectForm(issue_advsearch_page.FormHandler,
                           constants.ISSUE_ADVSEARCH_FORM_URL,
                           does_write=False) # Can be used when read-only.

    issue_search_tips = issuetips.IssueSearchTips(
      self.conn_pool, self.demetrius_persist,
      self.dit_persist, self.universal_ezt_data)
    self._SetupProjectPage(issue_search_tips.Handler,
                           constants.ISSUE_TIPS_PAGE_URL)

    attachment_page = issueattachment.AttachmentPage(
      self.conn_pool, self.demetrius_persist,
      self.dit_persist, self.universal_ezt_data)
    self._SetupProjectPage(attachment_page.Handler,
                           constants.ISSUE_ATTACHMENT_PAGE_URL)

    issue_admin_page = issueadmin.ProjectAdminIssues(
      self.conn_pool, self.demetrius_persist,
      self.dit_persist, self.universal_ezt_data)
    self._SetupProjectPage(issue_admin_page.Handler,
                           constants.ADMIN_ISSUES_PAGE_URL)
    self._SetupProjectForm(issue_admin_page.FormHandler,
                           constants.ADMIN_ISSUES_FORM_URL)
    """
