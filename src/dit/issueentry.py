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

"""Classes that implement the entry of new issues into DIT.
Summary of page classes:
  IssueEntry: Display a simple form for issue entry and process it.
  IssueOptionsFeed: Feed describing all issue labels and statuses.

Note that feed are sent in JSON (JavaScript Object Notation) format.
"""

import time

from ezt import ezt

from common import http
from common import post
from common import ezt_google

import framework.helpers

import demetrius.helpers
import demetrius.constants
import demetrius.permissions

import dit.helpers
import dit.pageclasses
import dit.constants
import dit.permissions



class IssueEntry(dit.pageclasses.DITPage):
  """IssueEntry shows a page with a simple form to enter a new issue."""

  _PAGE_TEMPLATE = 'dit/issue-entry-page.ezt'
  _MAIN_TAB_MODE = demetrius.constants.MAIN_TAB_ISSUES

  def AssertBasePermission(self, req_info):
    """Check whether the user has any permission to visit this page.

    Args:
      req_info: commonly used info parsed from the request.
    """

    dit.pageclasses.DITPage.AssertBasePermission(self, req_info)
    if not req_info.tool_perms.Check(dit.permissions.ENTER_COMMENT):
      raise demetrius.permissions.PermissionException(
        'You are not allowed to enter an issue')

  def EarlyPageProcessing(self, request, req_info):
    """Start getting some data while the user is being authenticated."""
    return self.MakePromise(
      self.dit_persist.GetProjectConfig, req_info.project_name)

  def GatherPageData(self, request, req_info):
    """Build up a dictionary of data values to use when rendering the page.

    Args:
      request: the HTTP request being processed.
      req_info: commonly used info parsed from the request.

    Returns: dict of values used by EZT for rendering almost all DIT pages.
    """
    config = req_info.early_promise.WaitAndGetValue()

    # In addtion to checking perms, we need to only offer meta-data editing
    # to project owner and members, not site admins who are not themselves
    # involved in this project.
    user_id = req_info.logged_in_user_id
    is_member = (user_id and
                 (user_id in req_info.project.owner_ids_list() or
                  user_id in req_info.project.member_ids_list()))
    offer_meta = (req_info.tool_perms.Check(dit.permissions.ENTER_METADATA) and
                  is_member)

    # TODO: these should come from project issue config.
    if offer_meta:
      wkp = config.well_known_prompts(config.default_prompt_for_developers())
      wkp_list = config.get_developer_prompts()
      initial_status = 'Accepted'
    else:
      wkp = config.well_known_prompts(config.default_prompt_for_users())
      wkp_list = config.get_user_prompts()
      initial_status = 'New'  # Note: won't actually be in HTML page.
     
    allow_attachments = (req_info.project.attachment_bytes_used() <
                         dit.constants.ISSUE_ATTACHMENTS_QUOTA_SOFT)

    page_data = {
      'issue_tab_mode': 'issueEntry',
      'initial_summary': req_info.GetParam(
        'summary', demetrius.constants.PROMPT_SUMMARY),
      'prompt_summary': demetrius.constants.PROMPT_SUMMARY,
      'must_edit_summary': ezt.boolean(True),
      # For now, always set initial summary to "Enter one-line summary"
      # and require the user to edit it.  Later, this will be customizable.

      'initial_description': req_info.GetParam('comment',
                                               wkp.prompt_text().replace('\\n', '\n')),
      'prompt_name': req_info.GetParam('prompt_name', wkp.prompt_name()),
      'all_prompts_list': wkp_list,
      'initial_status': req_info.GetParam('status', initial_status),
      'initial_owner': req_info.GetParam('owner',
                                         req_info.logged_in_user.edit_name),
      'initial_cc': req_info.GetParam('cc', ''),

      'offer_meta': ezt.boolean(offer_meta),
      'allow_attachments': ezt.boolean(allow_attachments),
      'errors': req_info.errors or ezt_google.EZTError(),
      }

    # TODO: these should come from project issue config.
    default_labels = ['Type-Defect', 'Priority-Medium']
    page_data.update(demetrius.helpers.BuildLabelDefaults(
      req_info, label_list=default_labels))

    post.URLCommandAttacksEncode(page_data, req_info.logged_in_user_id)
    return page_data

  def EarlyFormProcessing(self, request, req_info):
    """Start getting some data while the user is being authenticated."""
    return framework.helpers.Promise(
      self.dit_persist.GetProjectConfig, req_info.project_name)

  def ProcessForm(self, request, req_info):
    """Process the issue entry form.

    Args:
      request: the HTTP request being processed.
      req_info: commonly used info parsed from the request.
    """
    

    errors = ezt_google.EZTError()
    (_, summary, comment, status,
     owner_username, owner_id, cc_usernames, unused_cc_usernames_remove,
     cc_ids, unused_cc_ids_remove,
     labels, unused_labels_remove, prompt_name, attachments,
     post_data) = dit.helpers.ParseIssueRequest(
      request, self.conn_pool, self.demetrius_persist)
    if 'status' not in post_data:
      # User could not enter any metadata, use defaults instead.
      # TODO: prompt-specific defaults
      status = 'New'
      labels = ['Type-Defect', 'Priority-Medium']
      print labels

    reporter_id = req_info.logged_in_user_id
    post.URLCommandAttacksCheck(post_data, req_info.logged_in_user_id)

    if not summary.strip():
      errors.summary = 'Summary is required'
      print errors.summary

    if not comment.strip():
      errors.comment = 'A description is required'
      print errors.comment

    if not dit.helpers.UsersAreInProject(req_info.project, owner_id, cc_ids):
      errors.usernames = 'Invalid username for owner or CC'
      print errors.username
      
    config = req_info.early_promise.WaitAndGetValue()
    
    if not errors.AnyErrors():
      self.demetrius_persist.LockProject(req_info.project_name)
      try:
        try:
          if attachments:
            new_bytes_used = dit.helpers.CheckAttachmentQuota(
              req_info.project, attachments)

          prompt_text = ''
          for wkp in config.well_known_prompts_list():
            if wkp.prompt_name() == prompt_name:
              prompt_text = wkp.prompt_text()
          marked_comment = _MarkupIssueCommentOnInput(comment, prompt_text)
          has_star = 'star' in post_data and post_data['star'] == ['1']

          new_issue_id = self.dit_persist.CreateIssueInLockedProject(
            req_info.project, summary, status, owner_id, cc_ids,
            labels, reporter_id, self.demetrius_persist,
            marked_comment, self.conn_pool, attachments=attachments,
            index_now=not has_star)

          if has_star:
            self.dit_persist.SetStarInLockedProject(
              req_info.project, new_issue_id, reporter_id, True,
              self.conn_pool)

          if attachments:
            self.demetrius_persist.UpdateLockedProject(
              req_info.project_name, self.conn_pool,
              attachment_bytes_used=new_bytes_used)

        except dit.helpers.OverAttachmentQuota:
          errors.attachments = 'Project attachment quota exceeded.'

      finally:
        self.demetrius_persist.UnlockProject(req_info.project_name)

    if errors.AnyErrors():
      errors.any_errors = True
      req_info.PrepareForSubrequest(
        req_info.project_name, errors, summary=summary, status=status,
        owner=owner_username, cc=', '.join(cc_usernames),
        comment=comment, labels=labels)
      self.Handler(request, req_info=req_info)
      return

    detail_url = framework.helpers.FormatAbsoluteURL(
      req_info, dit.constants.ISSUE_DETAIL_PAGE_URL, request,
      id=new_issue_id)

    dit.helpers.SendIssueChangeNotification(
      req_info.project_name, new_issue_id, comment,
      reporter_id, 0, detail_url, self.worktable)

    url = framework.helpers.FormatAbsoluteURL(
      req_info, dit.constants.ISSUE_LIST_PAGE_URL, request,
      thanks=new_issue_id, ts=int(time.time()))
    http.SendRedirect(url, request)


class IssueOptionsFeed(dit.pageclasses.DITPage):
  """XML and JSON feed describing all issue statuses, labels, and members."""

  _PAGE_TEMPLATE = 'dit/issue-options-feed.ezt'

  def GatherPageData(self, request, req_info):
    """Build up a dictionary of data values to use when rendering the page.

    Args:
      request: the HTTP request being processed.
      req_info: commonly used info parsed from the request.

    Returns: dict of values used by EZT for rendering almost all DIT pages.
    """

    self.content_type = 'application/x-javascript; charset=UTF-8'

    page_data = demetrius.helpers.BuildProjectMembers(
        req_info.project, self.demetrius_persist,  self.conn_pool)
    config = dit.helpers.BuildProjectIssuesConfig(req_info.project,
                                                  self.dit_persist)
    page_data.update(config)
    return page_data

def _MarkupIssueCommentOnInput(content, prompt_text):
  """Return HTML for the content of an issue description or comment.

  Args:
    content: the text sumbitted by the user, any user-entered markup
             has already been escaped.
    prompt_text: the initial text that was put into the textarea.

  Returns: The comment content text with prompt lines highlighted.
  """
  prompt_lines = prompt_text.split('\n')
  prompt_lines = [pl.strip() for pl in prompt_lines if pl.strip()]

  lines = post.SafeForHTML(content).split('\n')
  lines = [_MarkupIssueCommentLineOnInput(l, prompt_lines)
           for l in lines]
  return '\n'.join(lines)


def _MarkupIssueCommentLineOnInput(line, prompt_lines):
  """Markup one line of an issue comment that was just entered.

  Args:
    line: string containing one line of the user-entered comment.
    prompt_lines: list of strings for the text of the prompt lines.

  Returns: The same user-entered line, or that line highlighted to
           indicate that it came from the prompt.

  Some markup work is done on before the comment is stored in BT so
  that later rendering is faster and because the prompt is only known
  at the time the input is processed.
  """

  if line.strip() in prompt_lines:
    line = '<b>' + line.strip() + '</b>'
  return line


class WKP_Tuple:
    
    def __init__(self):
        self.key = ''
        self.value = ''
        
    def key(self):
        return self.key
    
    def value(self):
        return self.value