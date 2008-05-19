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

"""Classes that implement the issue detail page and related forms.

Summary of classes:
  IssueDetail: Show one issue in detail w/ all metadata and comments, and
               process additional comments or metadata changes on it.
  SetStarForm: Record the user's desire to star or unstar an issue.
"""

import time
import sets

from ezt import ezt

from twisted.python import log

from common import http
from common import post
from common import ezt_google

from framework import artifactlist
import framework.helpers
import framework.constants

import demetrius.helpers
import demetrius.permissions
import demetrius.constants
import demetrius.persist

import dit.helpers
import dit.constants
from dit import persist
from dit import permissions
import dit.pageclasses


class IssueDetail(dit.pageclasses.DITPage):
  """IssueDetail is a page that shows the details of one issue."""

  _PAGE_TEMPLATE = 'dit/issue-detail-page.ezt'
  _MAIN_TAB_MODE = demetrius.constants.MAIN_TAB_ISSUES

  def _GetEarlyIssue(self, request, req_info):
    """Retrieve the current issue."""
    issue_id = req_info.GetIntParam('id')
    issue, ts = self.dit_persist.GetIssue(req_info.project_name, issue_id)
    return issue

  def _GetEarlyComments(self, request, req_info):
    """Retrieve the comments on the current issue."""
    issue_id = req_info.GetIntParam('id')
    issue = self.dit_persist.GetCommentsForIssueId(
      req_info.project_name, issue_id)
    return issue

  def EarlyPageProcessing(self, request, req_info):
    """Start getting some data while the user is being authenticated."""
    issue_promise = self.MakePromise(
      self._GetEarlyIssue, request, req_info)
    comments_promise = self.MakePromise(
      self._GetEarlyComments, request, req_info)
    config_promise = self.MakePromise(
      self.dit_persist.GetProjectConfig, req_info.project_name)
    return issue_promise, comments_promise, config_promise

  def GatherPageData(self, request, req_info):
    """Build up a dictionary of data values to use when rendering the page.

    Args:
      request: the HTTP request being processed.
      req_info: commonly used info parsed from the request.

    Returns: dict of values used by EZT for rendering almost all DIT pages.
    """

    issue_id = req_info.GetIntParam('id')
    issue_promise, comments_promise, config_promise = req_info.early_promise
    issue = issue_promise.WaitAndGetValue()
    if issue is None:
      raise framework.helpers.NoSuchPageException()

    if not demetrius.permissions.CanView(
      req_info.logged_in_user_id, req_info.demetrius_perms,
      issue, issue.reporter_id()):
      raise demetrius.permissions.PermissionException(
        'You are not allowed to view this issue')

    star_promise = self.MakePromise(
      self.dit_persist.IsStarredBy, req_info.project_name, issue.id(),
      req_info.logged_in_user_id)

    config = config_promise.WaitAndGetValue()

    flipper_promise = self.MakePromise(
      _Flipper, req_info, self.dit_persist, self.demetrius_persist, config)

    comments = comments_promise.WaitAndGetValue()

    proxies_by_id = framework.helpers.MakeAllUserIDProxies(
      self.conn_pool, self.demetrius_persist, [issue.owner_id()], issue.cc_ids_list(),
      [c.user_id() for c in comments])

    issue_proxy = dit.helpers.IssuePBProxy(
      issue, self.conn_pool, proxies_by_id)
    open_ref_issues, closed_ref_issues = self._GetReferencedIssues(
      req_info.project_name, comments)
    description_proxy = dit.helpers.CommentPBProxy(
      comments[0], self.conn_pool, proxies_by_id[comments[0].user_id()],
      open_ref_issues, closed_ref_issues, req_info.logged_in_user_id,
      req_info.tool_perms)
    comment_proxies = [dit.helpers.CommentPBProxy(
                         c, self.conn_pool, proxies_by_id[c.user_id()],
                         open_ref_issues, closed_ref_issues,
                         req_info.logged_in_user_id, req_info.tool_perms)
                       for c in comments[1:]]

    starred = star_promise.WaitAndGetValue()

    allow_attachments = (req_info.project.attachment_bytes_used() <
                         dit.constants.ISSUE_ATTACHMENTS_QUOTA_SOFT)

    req_info.col_spec = artifactlist.GetColSpec(
      req_info, config, dit.constants.DEFAULT_COL_SPEC)

    back_to_list_url = self._FormatIssueListURL(req_info, request, config)
    if dit.constants.JUMP_RE.match(req_info.query):
      back_to_list_url = None

    initial_summary = req_info.GetParam('summary')
    if not initial_summary:
      initial_summary = post.UndoSafeForHTML(issue_proxy.summary)

    flipper = flipper_promise.WaitAndGetValue()

    page_data = {
      'issue_tab_mode': 'issueDetail',
      'issue': issue_proxy,
      'description': description_proxy,
      'comments': comment_proxies,

      'flipper': flipper,
      'starred': ezt.boolean(starred),

      'pagegen': str(long(time.time() * 1000000)),

      # For deep linking and input correction after a failed submit.
      'initial_summary': initial_summary,
      'initial_comment': req_info.GetParam('comment', ''),
      'initial_status': req_info.GetParam('status', issue_proxy.status),
      'initial_owner': req_info.GetParam('owner', issue_proxy.owner.edit_name),
      'initial_cc': req_info.GetParam('cc',
                                      ', '.join([pb.edit_name
                                                 for pb in issue_proxy.cc])),

      'errors': req_info.errors or ezt_google.EZTError(),
      'show_update_form': req_info.errors,
      'allow_attachments': ezt.boolean(allow_attachments),
      'colspec': req_info.col_spec,
      'back_to_list_url': back_to_list_url,
    }

    page_data.update(demetrius.helpers.BuildLabelDefaults(
      req_info, label_list=issue.labels_list()))

    post.URLCommandAttacksEncode(page_data, req_info.logged_in_user_id)
    return page_data

  def _GetReferencedIssues(self, project_name, comments):
    """Return lists of open and closed issues referenced by these comments."""
    refs = sets.Set()
    for c in comments:  # Parse "issue 123" references out of all comments.
      for match in dit.constants.ISSUE_REF_RE.finditer(c.content()):
        refs.add(int(match.group(2)))

    log.msg('refs = %s' % refs)
    open_issues, closed_issues = self.dit_persist.GetOpenAndClosedIssues(
      project_name, refs)
    return open_issues, closed_issues

  def EarlyFormProcessing(self, request, req_info):
    """Start getting some data while the user is being authenticated."""
    return self.MakePromise(
      self.dit_persist.GetProjectConfig, req_info.project_name)

  def ProcessForm(self, request, req_info):
    """Process the posted issue update form.

    Args:
      request: the HTTP request being processed.
      req_info: commonly used info parsed from the request.
    """

    errors = ezt_google.EZTError()
    (issue_id, summary, comment, status,
     owner_username, owner_id,
     cc_usernames, unused_cc_usernames_remove, cc_ids, unused_cc_ids_remove,
     labels, unused_labels_remove, unused_prompt, attachments,
     post_data) = dit.helpers.ParseIssueRequest(
      request, self.conn_pool, self.demetrius_persist)

    # Check that the user is logged in; anon users cannot update issues.
    if req_info.logged_in_user_id is None:
      log.msg('user was not logged in, cannot update issue')
      http.BadRequest(request)
      return

    # Check that the user has permission to add a comment, and to enter
    # metadata if they are trying to do that.
    if not req_info.tool_perms.Check(dit.permissions.ENTER_COMMENT):
      log.msg('user has no permission to add issue comment')
      http.BadRequest(request)
      return

    if not req_info.tool_perms.Check(dit.permissions.ENTER_METADATA):
      if summary or cc_ids or labels or status or owner_id:
        log.msg('user has no permission to edit issue metadata')
        http.BadRequest(request)
        return

    page_generation_time = long(post_data['pagegen'][0])

    reporter_id = req_info.logged_in_user_id
    post.URLCommandAttacksCheck(post_data, reporter_id)
    
    if not dit.helpers.UsersAreInProject(req_info.project, owner_id, []):
      errors.usernames = 'Invalid username for the user assigned to the issue. That user is not a member of the project.'

    if not dit.helpers.CCUsersAreInProject(req_info.project, cc_ids):
      errors.usernames = 'Invalid username(s) for the users notified about the issue. At least one user you specified is not a project member.'
    
    if not errors.AnyErrors():
      self.demetrius_persist.LockProject(req_info.project_name)
      try:
        try:
          if attachments:
            new_bytes_used = dit.helpers.CheckAttachmentQuota(
              req_info.project, attachments)

          if 'summary' not in post_data:
            # User is not able to edit any metadata
            update_tuples = None
          else:
            update_tuples = self.dit_persist.UpdateIssueInLockedProject(
              req_info.project, issue_id, summary, status, owner_id, cc_ids,
              labels, self.conn_pool, None, page_gen_ts=page_generation_time)

          self.dit_persist.CreateIssueCommentInLockedProject(
            req_info.project, issue_id, reporter_id, comment,
            self.conn_pool, update_tuples=update_tuples,
            attachments=attachments)

          if attachments:
            self.demetrius_persist.UpdateLockedProject(
              req_info.project_name, self.conn_pool,
              attachment_bytes_used=new_bytes_used)

        except dit.helpers.OverAttachmentQuota:
          errors.attachments = 'Project attachment quota exceeded.'

      finally:
        self.demetrius_persist.UnlockProject(req_info.project_name)

    if errors.AnyErrors():
      req_info.PrepareForSubrequest(
        req_info.project_name, errors, summary=summary, status=status,
        owner=owner_username, cc=', '.join(cc_usernames),
        comment=comment, labels=labels, id=issue_id)
      self.Handler(request, req_info=req_info)
      return

    detail_url = framework.helpers.FormatAbsoluteURL(
      req_info, dit.constants.ISSUE_DETAIL_PAGE_URL, request,
      id=issue_id)

    all_comments = self.dit_persist.GetCommentsForIssueId(
      req_info.project_name, issue_id)
    sequence_num = len(all_comments) - 1

    dit.helpers.SendIssueChangeNotification(
      req_info.project_name, issue_id, comment, reporter_id,
      sequence_num, detail_url, self.worktable)

    config = req_info.early_promise.WaitAndGetValue()

    req_info.can = int(post_data['can'][0])
    req_info.query = post_data['q'][0]
    req_info.col_spec = post_data['colspec'][0]
    req_info.sort_spec = post_data['sort'][0]
    req_info.start = int(post_data['start'][0])
    req_info.num = int(post_data['num'][0])
    url = self._FormatIssueListURL(
      req_info, request, config, updated=issue_id, ts=int(time.time()))
    http.SendRedirect(url, request)

  def _FormatIssueListURL(self, req_info, request, config, **kw):
    """Format a link back to list view as configured by user."""
    if not dit.constants.JUMP_RE.match(req_info.query):
      if req_info.query:
        kw['q'] = req_info.query
      if req_info.can and req_info.can != 2:
        kw['can'] = req_info.can
    def_col_spec = config.default_col_spec() or dit.constants.DEFAULT_COL_SPEC
    if req_info.col_spec and req_info.col_spec != def_col_spec:
      kw['colspec'] = req_info.col_spec
    if req_info.sort_spec:
      kw['sort'] = req_info.sort_spec
    if req_info.start:
      kw['start'] = req_info.start
    if req_info.num != dit.constants.DEFAULT_RESULTS_PER_PAGE:
      kw['num'] = req_info.num

    host = request.received_headers['host']
    param_strings = ['%s=%s' % (k, v) for k, v in kw.items()]
    relative_url = dit.constants.ISSUE_LIST_PAGE_URL
    if param_strings:
      relative_url += '?' + '&'.join(param_strings)
    url = 'http://%s/p/%s%s' % (host, req_info.project_name, relative_url)
    return url

class SetStarForm(dit.pageclasses.DITPage):
  """Star or unstar the specified issue for the logged in user."""

  _PAGE_TEMPLATE = 'dit/set-star-form.ezt'

  def AssertBasePermission(self, req_info):
    dit.pageclasses.DITPage.AssertBasePermission(self, req_info)
    if not req_info.tool_perms.Check(permissions.SET_STAR):
      raise demetrius.permissions.PermissionException(
        'You are not allowed to star issues')


  def GatherPageData(self, request, req_info):
    """Build up a dictionary of data values to use when rendering the page.

    Args:
      request: the HTTP request being processed.
      req_info: commonly used info parsed from the request.

    Returns: dict of values used by EZT for rendering almost all DIT pages.
    """

    issue_id = req_info.GetIntParam('issueid')
    starred = req_info.GetIntParam('starred')

    self.demetrius_persist.LockProject(req_info.project_name)
    try:
      self.dit_persist.SetStarInLockedProject(
        req_info.project, issue_id, req_info.logged_in_user_id, starred,
        self.conn_pool)
    finally:
      self.demetrius_persist.UnlockProject(req_info.project_name)

    return {
      'star_value': starred,
      }


class _Flipper(object):
  """Helper class for user to flip among issues within a search result."""

  def __init__(self, req_info, dit_persist, demetrius_persist, config):
    """Store info for issue flipper widget (prev & next navigation).

    Args:
      req_info: commonly used info parsed from the request.
      dit_persist: DITPersist interface to storage backends.
      demetrius_persist: DemetriusPersist interface to storage backends.
      config: ProjectIssueConfig object.
    """

    # Check if the user entered a specific issue ID of an existing issue
    if dit.constants.JUMP_RE.match(req_info.query):
      self.show = ezt.boolean(False)
      return

    result_ids = dit.helpers.SearchIssueIDs(req_info, dit_persist,
                                            demetrius_persist, config)
    cur_issue_id = req_info.GetIntParam('id')

    cur_issue_index = -1
    try:
      cur_issue_index = result_ids.index(cur_issue_id)
    except ValueError:
      pass

    if cur_issue_index == -1 or len(result_ids) == 1:
      # The user probably edited the URL, or bookmarked an issue
      # in a search context that no longer matches the issue.
      self.show = ezt.boolean(False)
    else:
      self.show = True
      self.current = cur_issue_index + 1
      self.total_count = len(result_ids)
      self.prev_url = ''
      self.next_url = ''

      if cur_issue_index > 0:
        prev_id = result_ids[cur_issue_index - 1]
        self.prev_url = framework.helpers.FormatURL(
          req_info, dit.constants.ISSUE_DETAIL_PAGE_URL.split('/')[-1],
          id=prev_id)

      if cur_issue_index < len(result_ids) - 1:
        next_id = result_ids[cur_issue_index + 1]
        self.next_url = framework.helpers.FormatURL(
          req_info, dit.constants.ISSUE_DETAIL_PAGE_URL.split('/')[-1],
          id=next_id)


  def DebugString(self):
    """Return a string representation useful in debugging."""
    if self.show:
      return 'on %s of %s; prev_url:%s; next_url:%s' % (
        self.current, self.total_count, self.prev_url, self.next_url)
    else:
      return 'invisible flipper(show=%s)' % self.show


class IssueCommentDeletion(dit.pageclasses.DITPage):
  """Form handler that allows user to delete/undelete comments."""

  def ProcessForm(self, request, req_info):
    """Process the form that un/deletes an issue comment.

    Args:
      request: the HTTP request being processed.
      req_info: commonly used info parsed from the request.
    """
    project_name = req_info.project_name
    post_data = post.ProcessPOSTBody(
      request, framework.constants.MAX_POST_BODY_SIZE)
    log.msg('post_data = %s' % post_data)
    issue_id = int(post_data['id'][0])
    sequence_num = int(post_data['sequence_num'][0])
    delete = post_data['mode'][0] == '1'
    post.URLCommandAttacksCheck(post_data, req_info.logged_in_user_id)

    all_comments = self.dit_persist.GetCommentsForIssueId(
      project_name, issue_id)
    log.msg('comments on %s are: %s' % (issue_id, all_comments))
    comment = all_comments[sequence_num]

    if not demetrius.permissions.CanDelete(
      req_info.logged_in_user_id, req_info.tool_perms, comment,
      creator_user_id=comment.user_id()):
      raise demetrius.permissions.PermissionException('Cannot delete comment')

    self.dit_persist.SoftDeleteComment(
      project_name, issue_id, sequence_num, req_info.logged_in_user_id,
      delete=delete)

    url = framework.helpers.FormatAbsoluteURL(
      req_info, dit.constants.ISSUE_DETAIL_PAGE_URL, request,
      id=issue_id)
    http.SendRedirect(url, request)
