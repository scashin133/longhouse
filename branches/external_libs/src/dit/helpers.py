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

"""Helper functions and classes used by the Demetrius Issue Tracker pages.

This module exports two kinds of items:
  1. Functions that are reused in multiple servlets or other modules.
  2. Proxy classes that wrap PBs or other objects for use with EZT.
"""

import time
import cgi
import re
import urllib

from ezt import ezt

from common import post
from common import ezt_google
from common import timestr
from bo import dit_pb

from framework import artifact
from framework import artifactlist
import framework.helpers
import framework.constants

import demetrius.constants
import demetrius.permissions

from dit import persist
import dit.constants
#from bo import worktable_pb


# Accessors for sorting built-in fields.
_SORTABLE_FIELDS = {
  'id' : dit_pb.Issue.id,
  'owner' : dit_pb.Issue.owner_id, # TODO: sort by username, not id.
  'reporter' : dit_pb.Issue.reporter_id, # TODO: sort by username, not id.
  'summary' : dit_pb.Issue.summary,
  'stars' : dit_pb.Issue.star_count,
  'opened' : dit_pb.Issue.opened_timestamp,
  'closed' : dit_pb.Issue.closed_timestamp,
  'modified' : dit_pb.Issue.modified_timestamp,
  'status': dit_pb.Issue.status,
  }


# Accessors for sorting built-in fields, in descending order.
_SORTABLE_FIELDS_DESCENDING = {
  'id' : lambda x: -x.id(),
  'owner' : lambda x: -x.owner_id(), # TODO: sort by username
  'reporter' : lambda x: -x.reporter_id(), # TODO: sort by username
  'summary' : lambda x: artifactlist.DescendingStr(x.summary()),
  'stars' : lambda x: -x.star_count(),
  'opened' : lambda x: -x.opened_timestamp(),
  'closed' : lambda x: -x.closed_timestamp(),
  'modified' : lambda x: -x.modified_timestamp(),
  'status': lambda x: artifactlist.DescendingStr(x.status()),
  }


def checkMultipleLabels(exclusive_label_prefixes_list, labels):
    """Checks the labels to see if there are mutliples of exclusive labels
    
    Args:
        exclusive_label_prefixes: list of labels that should only exist once.
        labels: the labels to test
    
    Return: boolean true if there are multiple exclusive labels (making it a bad issue)    
    """
    label_prefixes = {}

    for label in labels:
      split_label = label.split("-")
      first_element = split_label[0].lower()

      try:
          label_prefixes[first_element] = label_prefixes[first_element] = label_prefixes[first_element] + 1
      except KeyError:
          label_prefixes[first_element] = 1

    for excl_label in excl_labels:
      try:
        if(label_prefixes[excl_label] > 1):
          return "true"
      except KeyError:
        continue

    return "false"

    

def BuildProjectIssuesConfig(project, dit_persist):
  """Gather data for the issue section of a project admin page.

  Args:
    project: the current Project PB.
    dit_persist: DITPage interface to storage backends.

  Returns: project info in a dict suitable for EZT.
  """

  canonical_name = project.project_name().lower()
  project_config = dit_persist.GetProjectConfig(canonical_name)
  open_statuses = []
  closed_statuses = []
  for wks in project_config.well_known_statuses_list():
    item = ezt_google.EZTItem(name=wks.status(),
                              name_padded=ezt_google.ljust(wks.status(), 20),
                              docstring=wks.status_docstring())
    if persist.MeansOpenInProject(wks.status(), project_config):
      open_statuses.append(item)
    else:
      closed_statuses.append(item)

  issue_labels = []
  for wkl in project_config.well_known_labels_list():
    item = ezt_google.EZTItem(name=wkl.label(),
                              name_padded=ezt_google.ljust(wkl.label(), 20),
                              docstring=wkl.label_docstring())
    issue_labels.append(item)

  # TODO: allow canned queries to be edited

  prompts = []
  for p in project_config.well_known_prompts_list():
    item = ezt_google.EZTItem(index=len(prompts),
                              prompt_name=JSEscape(p.prompt_name()),
                              prompt_text=JSEscape(p.prompt_text()),
                              prompt_text_value=p.prompt_text())
    prompts.append(item)

  config_data = {
    'open_statuses': open_statuses,
    'closed_statuses': closed_statuses,
    'issue_labels': issue_labels,
    'excl_prefixes': [prefix.lower() for prefix in
                      project_config.exclusive_label_prefixes_list()],
    'prompts': prompts,
    }
  config_data.update(artifactlist.BuildListPrefs(
    project_config, dit.constants.DEFAULT_COL_SPEC))
  return config_data


def JSEscape(string):
  """Return the given string escaped for safe use in Javascript code."""
  s = cgi.escape(string)
  s = s.replace('\r', '')
  s = s.replace('\n', '\\n')
  return s


def ParseIssueRequest(request, conn_pool, demetrius_persist):
  """Parse all the possible arguments out of the request.

  Args:
    request: the HTTP request being processed.
    conn_pool: ConnectionPool object that interfaces to AuthSub.
    demetrius_persist: DemetriusPersist interface to storage backends.

  Returns: a tuple with all parsed information.
  """
  

  # Note: post_data is *not* a typical CGI param dictionary; it is
  # a cgi.FieldStorage object.
  post_data = post.ProcessMultipartPOSTBody(
    request, framework.constants.MAX_POST_BODY_SIZE)
  if post_data is None:
    # An error occurred and the response was generated. We're done.
    raise framework.helpers.AlreadySentResponse()

  summary = ''
  comment = ''
  status = ''
  owner_username = ''
  cc_username_strs = []
  cc_emails = []
  cc_usernames = []
  cc_usernames_remove = []
  issue_id = None
  prompt_name = ''

  if post_data.has_key('id'): issue_id = int(post_data.getfirst('id'))
  summary = post_data.getfirst('summary', summary)
  comment = post_data.getfirst('comment', comment)
  status = post_data.getfirst('status', status)
  if post_data.has_key('cc'):
    cc_username_strs = post_data.getfirst('cc').split(',')
    cc_emails = [framework.helpers.ConvertEditNameToEmail(cc.strip())
                 for cc in cc_username_strs if cc.strip()]
  prompt_name = post_data.getfirst('promptname', prompt_name)
  label_strs = post_data.getlist('label')
  labels = []
  labels_remove = []
  for label in label_strs:
    lab = label.strip()
    if lab.startswith('-'):
      labels_remove.append(lab[1:])
    elif lab:  # Note that empty labels are skipped.
      labels.append(lab)

  # TODO: change from numbered fields to a multi-valued field.
  attachments = []
  for i in xrange(1, 16):
    if post_data.has_key('file%s' % i):
      item = post_data['file%s' % i]
      if '\\' in item.filename: # IE insists on giving us the whole path.
        item.filename = item.filename[item.filename.rindex('\\') + 1:]
      attachments.append((item.filename, item.value))

  emails_to_lookup = []
  for cc_email in cc_emails:
    if cc_email.startswith('-'):
      cc_email = cc_email[1:]
    emails_to_lookup.append(cc_email)

  if post_data.has_key('owner'):
    owner_username = post_data.getfirst('owner', owner_username).strip()
    owner_email = framework.helpers.ConvertEditNameToEmail(owner_username)
    if owner_username == '':
      owner_id = framework.constants.NO_USER_SPECIFIED
    else:
      emails_to_lookup.append(owner_email)
  else:
    owner_id = framework.constants.NO_USER_SPECIFIED

  #all_user_ids = conn_pool.GetUserIDBatch(emails_to_lookup)
  all_user_ids = {}
  for email_addr in emails_to_lookup:
      all_user_ids[email_addr] = demetrius_persist.LookupUserIdByEmail(email_addr)
  if owner_username:
    owner_id = all_user_ids[owner_email]

  cc_ids = []
  cc_ids_remove = []
  for cc in cc_username_strs:
    cc = cc.strip()
    cc_email = framework.helpers.ConvertEditNameToEmail(cc)
    if cc.startswith('-'):
      cc_ids_remove.append(all_user_ids[cc_email[1:]])
      cc_usernames_remove.append(cc)
    elif cc: # skip blanks
      cc_ids.append(all_user_ids[cc_email])
      cc_usernames.append(cc)

  # Map the POST data into a traditional dict format.
  post_data_dict = {}
  for key in post_data.keys():
    post_data_dict[key] = post_data.getlist(key)

  return (issue_id, summary, comment, status,
          owner_username, owner_id,
          cc_usernames, cc_usernames_remove, cc_ids, cc_ids_remove,
          labels, labels_remove,
          prompt_name, attachments, post_data_dict)


def CCUsersAreInProject(project, cc_ids):
  for cc_id in cc_ids:
    if not UserIsInProject(project, cc_id):
      return False

  return True

def UsersAreInProject(project, owner_id, cc_ids):
  """Return True if all the given user IDs are project members.

  Args:
    project: the current Project PB.
    owner_id: the user id of the proposed issue owner.
    cc_ids: the user ids of the proposed users to be CC'd.

  It is OK to have None for the owner_id.  None is considered to be a member
  of every project so that issues can be unassigned.
  """

  if owner_id != framework.constants.NO_USER_SPECIFIED:
    if not UserIsInProject(project, owner_id):
      return False

  for cc_id in cc_ids:
    if not UserIsInProject(project, cc_id):
      return False

  return True


def UserIsInProject(project, user_id):
  """Return True if the given user_id is a project owner or member."""
  return (user_id in project.member_ids_list() or
          user_id in project.owner_ids_list())


def MarkupIssueCommentOnOutput(content, open_issues, closed_issues):
  """Return HTML for the content of an issue description or comment.

  Args:
    content: the stored text of an issue description or comment.
    open_issues: set of open issue referenced by any comment on this issue.
    closed_issues: set of closed issue referenced by any comment on this issue.

  Returns: issue text marked up as appropriate for the current request.

  The HTML differs from the stored comment markup because it applies
  search term highlighting, and auto-links certain references to other
  issues or VC changes.
  """

  open_dict = {}
  for issue in open_issues:
    open_dict[issue.id()] = issue

  closed_dict = {}
  for issue in closed_issues:
    closed_dict[issue.id()] = issue

  def _ReplaceIssueRef(match):
    prefix = match.group(1)
    issue_id = int(match.group(2))

    if issue_id in open_dict:
      summary = open_dict[issue_id].summary()
      css = ''
      extra_crossout = ''
    elif issue_id in closed_dict:
      summary = closed_dict[issue_id].summary()
      css = 'class=closed_ref'
      extra_crossout = ' '
    else:  # Don't link to non-existent issues.
      return '%s%d' % (prefix, issue_id)

    rollover = 'title="%s"' % ezt_google.FitString(summary, 0)[1]

    return ('<a %s %s href="detail?id=%d">%s%s%d%s</a>' %
            (rollover, css, issue_id,
             extra_crossout, prefix, issue_id, extra_crossout))

  markup = dit.constants.ISSUE_REF_RE.sub(_ReplaceIssueRef, content)
  return markup


def SearchIssues(req_info, dit_persist, config):
  """Search issues in current project and return a sorted list of issue PBs.

  Args:
    req_info: commonly used info parsed from the request, including query and
              sort spec.
    dit_persist: DITPage interface to storage backends.
    config: ProjectIssueConfig for the current project.

  Returns: a sorted list of issue PBs that satisfy the query.
  """

  if req_info.can == 1 and not req_info.query:
    issues = dit_persist.GetAllIssuesInProject(req_info.project_name)
  elif req_info.can == 2 and not req_info.query:
    issues = dit_persist.GetAllOpenIssuesInProject(req_info.project_name)
  else:
    canned_query = dit.constants.DEFAULT_CANNED_QUERIES[req_info.can - 1][1]
    # TODO: combine default canned queries with project-specific ones.
    issue_ids = dit_persist.SearchProjectCan(
      req_info.query, req_info.project_name, canned_query,
      req_info.logged_in_user, req_info)
    issues = dit_persist.GetIssuesByIDs(req_info.project_name, issue_ids)

  sorted_issues = artifactlist.SortArtifacts(
    req_info, issues, config, _SORTABLE_FIELDS, _SORTABLE_FIELDS_DESCENDING)

  return sorted_issues


def SearchIssueIDs(req_info, dit_persist, demetrius_persist, config):
  """Search the issues and return a sorted list of issue ids.

  Args:
    req_info: commonly used info parsed from the request, including query.
    dit_persist: DITPage interface to storage backends.
    demetrius_persist: DemetriusPersist interface to storage backends.
    config: ProjectIssueConfig for the current project.

  Returns: a sorted list of issue ids that satisfy the query.

  Note: In the simple, frequent cases, scanning the requested ids is much
  faster than searching for the Issue PBs.
  """

  if req_info.can == 1 and not req_info.query and not req_info.sort_spec:
    issue_ids = dit_persist.GetAllIssueIDsInProject(req_info.project_name,
                                                      demetrius_persist)
  elif req_info.can == 2 and not req_info.query and not req_info.sort_spec:
    issue_ids = dit_persist.GetAllOpenIssueIDsInProject(req_info.project_name)
  else:
    # The only way to properly sort the ids is to get and sort the issues.
    issues = SearchIssues(req_info, dit_persist, config)
    issue_ids = [issue.id() for issue in issues]

  return issue_ids


class IssuePBProxy(ezt_google.PBProxy):
  """Wrapper class that makes it easier to display an Issue via EZT."""

  def __init__(self, issue_pb, conn_pool, proxies_by_id, escape_html=True):
    """Store relevant values for later display by EZT.

    Args:
      issue_pb: An Issue business object.
      conn_pool: ConnectionPool object that interfaces to AuthSub.
      proxies_by_id: dict mapping user_ids to UserIDProxies.
      escape_html: If true, replace <, &, and " with HTML entities.
    """

    ezt_google.PBProxy.__init__(self, issue_pb)

    _TITLE_DISPLAY_CHARS = 300
    self.owner = proxies_by_id[issue_pb.owner_id()]
    self.cc = [proxies_by_id[cc_id] for cc_id in issue_pb.cc_ids_list()]
    self.labels = [artifact.LabelProxy(label)
                   for label in issue_pb.labels_list()]
    # TODO: sort by order of labels in project config

    self.summary = issue_pb.summary()
    self.summary_tooltip = None

    # Escape the summary.  Don't let EZT do it, because we will some
    # HTML in summaries in the future.  E.g., highlight search terms.
    # Or, if sending an email, make sure that it is not escaped.
    if escape_html and not issue_pb.summary_is_escaped():
      self.summary = post.SafeForHTML(issue_pb.summary())
    elif not escape_html and issue_pb.summary_is_escaped():
      self.summary = post.UndoSafeForHTML(issue_pb.summary())

    self.short_summary = self.summary

    if issue_pb.has_closed_timestamp():
      self.closed = timestr.ComputeAbsoluteDate(issue_pb.closed_timestamp())
    else:
      self.closed = ""


class CommentPBProxy(ezt_google.PBProxy):
  """Wrapper class that makes it easier to display an IssueComment via EZT."""

  def __init__(self, comment_pb, conn_pool, user_proxy,
               open_ref_issues, closed_ref_issues, logged_in_user_id,
               perms, escape_html=True):
    """Get IssueComment BO and make its fields available as attrs.

    Args:
      comment_pb: Comment business object.
      conn_pool: ConnectionPool object that interfaces to AuthSub.
      user_proxy: UserIDProxy for the user that entered the comment.
      open_ref_issues: list of open issues that may be referenced from
                       this comment
      closed_ref_issues: list of closed issues that may be referenced from
                         this comment
      logged_in_user_id: long int user id of logged in user.
      perms: tool-specific permissions that control deleting comments.
      escape_html: If true, replace <, &, and " with HTML entities.
    """

    ezt_google.PBProxy.__init__(self, comment_pb)

    self.creator = user_proxy
    time_tuple = time.localtime(comment_pb.timestamp())
    self.date_string = timestr.ComputeAbsoluteDate(comment_pb.timestamp())
    self.date_relative = timestr.ComputeRelativeDate(comment_pb.timestamp())
    self.date_tooltip = time.asctime(time_tuple)
    # Internet date time representation (RFC 3339)
    self.internet_date_time_string = timestr.GetInternetDateTimeString(
        comment_pb.timestamp())
    # TODO: make sure that dates and times are localized
    self.content = comment_pb.content()
    if not comment_pb.was_escaped():
      # We escape manually before sending to EZT so that we can mix in HTML.
      self.content = post.SafeForHTML(self.content)
    self.content = MarkupIssueCommentOnOutput(
      self.content, open_ref_issues, closed_ref_issues)
    self.attachments = [AttachmentPBProxy(attachment)
                        for attachment in comment_pb.attachments_list()]
    self.update_objs = [IssueUpdateObject(update_pb, comment_pb.was_escaped(),
                                          escape_html=escape_html)
                        for update_pb in comment_pb.updates_list()]

    if hasattr(comment_pb, "sequence"):
      self.sequence = comment_pb.sequence # BT timestamp order of comments
    self.is_deleted = comment_pb.has_deleted_by()
    self.can_delete = False
    if logged_in_user_id:
      self.can_delete = demetrius.permissions.CanDelete(
        logged_in_user_id, perms, comment_pb, comment_pb.user_id())
    self.visible = self.can_delete or not comment_pb.has_deleted_by()


class AttachmentPBProxy(ezt_google.PBProxy):
  """Wrapper class to make it easier to display issue attachments via EZT."""

  def __init__(self, attach_pb):
    """Get IssueAttachmentContent PB and make its fields available as attrs.

    Args:
      attach_pb: Attachment part of IssueComment business object.
    """

    ezt_google.PBProxy.__init__(self, attach_pb)
    self.filesizestr = ezt_google.BytesKbOrMb(attach_pb.filesize())

    self.url = 'attachment?aid=%s' % attach_pb.attachment_id()
    self.downloadurl = 'attachment?aid=%s&name=%s' % (
      attach_pb.attachment_id(),
      urllib.quote_plus(attach_pb.filename()))

    self.iconurl = '/images/generic.gif'


class IssueUpdateObject(object):
  """Wrapper class that makes it easier to display an IssueUpdate via EZT."""

  def __init__(self, update_pb, was_escaped, escape_html=True):
    """Get the info from the PB and put it into easily accessible attrs.

    Args:
      update_pb: Update part of an IssueComment business object.
      was_escaped: True if input was escaped on entry (OLD style).
      escape_html: If true, replace <, &, and " with HTML entities.
    """

    self.newvalue = update_pb.newvalue()
    if escape_html and not was_escaped:
      # We escape manually before sending to EZT so that we can mix in HTML.
      self.newvalue = post.SafeForHTML(self.newvalue)
    elif not escape_html and was_escaped:
      self.newvalue = post.UndoSafeForHTML(self.newvalue)

    field_id = update_pb.field()
    field_name = dit_pb.IssueComment_Updates._FIELD_ID_NAMES[field_id]
    self.field_name = field_name.capitalize()


def SendIssueChangeNotification(project_name, issue_id, comment_text,
                                commenter_id, sequence_num, detail_url,
                                worktable):
  """Notify all interested people that the given issue has been updated.

  Args:
    project_name: the name of the current project.
    issue_id: Issue number for the issue that was updated and saved.
    comment_text: String with safe, unmarked text of user's comment.
    commenter_id: long user id of the user who made the comment.
    sequence_num: index of the comment, 0 for initial issue descriptions.
    detail_url: URL for viewing the issue in detail.
    worktable: WorkTable instance used to queue up items for worker processes.

  Returns nothing.
  """
  # TODO(students): reimplement


def CheckAttachmentQuota(project, attachments):
  """Check the project's attachment storage quota.

  Args:
    project: Project BO  for the project being updated.
    attachment: a list of attachments being added to an issue.

  Returns:a the new number of bytes used.
  Exceptions: OverAttachmentQuota if project would go over quota.
  """

  total_attach_size = 0L
  for filename, content in attachments:
    total_attach_size += len(content)

  new_bytes_used = project.attachment_bytes_used() + total_attach_size
  quota = dit.constants.ISSUE_ATTACHMENTS_QUOTA_HARD
  if project.has_attachment_quota():
    quota = project.attachment_quota()
  if new_bytes_used > quota:
    raise OverAttachmentQuota(new_bytes_used - quota)
  return new_bytes_used


class Error(Exception):
  """Base class for errors from this module."""


class OverAttachmentQuota(Error):
  """Project will exceed quota if the current operation is allowed."""
