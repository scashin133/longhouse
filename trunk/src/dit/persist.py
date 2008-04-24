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

"""A set of functions that provide persistence for the Demetrius Issue Tracker.

This module provides functions to get, update, create, and (in some
cases) delete each type of DIT business object.  It provides a logical
persistence layer on top of our underlying storage.

Business objects are described in bo/dit.py.
"""


import time

from twisted.python import log

from common import post
from bo import dit_pb

from framework import user
from framework import artifactlist
#from framework import artifactpersist
#from codesite import framework
import framework.persist
import framework.constants
from framework import local_persist

#from codesite import dit
import dit.constants
from dit import issueindex

class DITPersist(object):
  """The persistence layer for all of Demetrius's data."""
  
  def __init__(self):
    """Initialize this object so that it is ready to use."""
    self.issue_index = issueindex.IssueIndex()
    self.project_indexes = {}
    self.current_issue_ids = {}
    self.issue_modified_timestamps = {}
    self.issue_comments = {}
    self.user_issue_stars = {}
    self.issue_user_stars = {}

  ### Issues
  
  def register_demetrius_persist(self, demetrius_persist):
    self.demetrius_persist = demetrius_persist
    
  def get_demetrius_persist(self):  
    return self.demetrius_persist
    
  def GetAllOpenIssuesInProject(self, project_name):
    """Special query to efficiently get all open issues in a project.

    This is the most common query because it is the default.

    Args:
      project_name: the name of the current project.

    Returns: a list of Issue business objects for all open issues.
    """

    open_issues = []
    x = 0
    project_issues = self.project_indexes.get(project_name, None)
    if(project_issues is None):
        return []
    else:
        #for issue in project_issues.values():
            #TODO: Add 'is_open()' method to issue() and filter by the result of that method
        return project_issues.values()

  def GetAllOpenIssueIDsInProject(self, project_name):
    """Return the list of open issue IDs only, not the actual issues."""
    #issues = self.GetAllOpenIssuesInProject(project_name)
    #return [issue.id() for issue in issues]
    open_issues = []
    x = 0
    project_issues = self.project_indexes.get(project_name, None)
    if(project_issues is None):
        return []
    else:
        #for issue in project_issues.values():
            #TODO: Add 'is_open()' method to issue() and filter by the result of that method
        #    open_issues[x] = issue
        #    x = x + 1
        #return open_issues
        return project_issues.keys()

  def GetAllIssuesInProject(self, project_name):
    """Special query to efficiently get ALL issues in a project.

    This will probably be the second most common query.

    Args:
      project_name: the name of the current project.

    Returns: a list of Issue business objects for all issues.
    """

    # Load and deserialize all issues, both open and closed.
    # TODO(students): reimplement this.
    
    return self.project_indexes.get(project_name, {}).values()

  def GetAllIssueIDsInProject(self, project_name, demetrius_persist):
    """Return the list of issue IDs only, not the actual issues."""
    return self.project_indexes.get(project_name, {}).keys()
    #if(project_issues is None):
    #    return []
    #else:
    #    return project_issues.keys()
    
  def GetIssue(self, project_name, issue_id):
    """Get one Issue BO from disk.

    Args:
      project_name: the name of the current project.
      issue_id: integer issue id with that project.

    Returns: (Issue business object, timestamp of last update)
    """
    # TODO(students): reimplement this.
    project_index = self.project_indexes.get(project_name)
    issue = project_index.get(issue_id)
    issue_ts = self.issue_modified_timestamps.get(project_name).get(issue_id)
    return issue, issue_ts
    
  def GetIssuesByIDs(self, project_name, issue_id_list):
    """Get all the requested issues.

    Args:
      project_name: the name of the current project.
      issue_id_list: list of integer issue ids for the requested issues.

    Returns: List of Issue business objects for the requested issues.
    """

    if len(issue_id_list) == 0: return []
    result = []
    x = 0
    project_index = self.project_indexes.get(project_name)
    for issue_id in project_index.keys():
        if(issue_id in issue_id_list):
            result[x] = project_index.get(issue_id)
            x = x + 1
    return result

  def GetOpenAndClosedIssues(self, project_name, issue_id_list):
    """Return the requested issues in separate open and closed lists."""
    if not issue_id_list:
      return [], []  # make one common case efficient

    open_issues = []
    closed_issues = []
    # TODO(students): reimplement this.

    return open_issues, closed_issues


  def CreateIssueInLockedProject(
    self, project, summary, status, owner_id, cc_ids, labels,
    reporter_id, demetrius_persist, marked_description, conn_pool,
    attachments=None, star_count=0, timestamp=None, index_now=True):
    """Create and store a new issue with all the given information.

    Args:
      project: the BO for the current project (must be locked).
      summary: one-line summary string summarizing this issue.
      status: string issue status value.  E.g., 'New'.
      owner_id: user id of the issue owner.
      cc_ids: list of user ids for users to be CC'd on changes.
      labels: list of label strings.  E.g., 'Priority-High'.
      reporter_id: user id of the user who reported the issue.
      demetrius_persist: DemetriusPersist interface to storage backends.
      marked_description: issue description with initial HTML markup.
      conn_pool: ConnectionPool object that interfaces to AuthSub.
      attachments: [(filename, contents),...] attachments uploaded at
                   the time the comment was made.
      star_count: number of users who have starred this issue.
      timestamp: time that the issue was entered, defaults to now.
      index_now: True if the issue should be updated in search engine.

    Returns: the integer id of the new issue.
    """
    project_name = project.project_name()
    config = self.GetProjectConfig(project_name)

    status = post.CanonicalizeLabel(status)
    labels = [post.CanonicalizeLabel(l) for l in labels]

    issue = dit_pb.Issue()
    
    project_issues = self.project_indexes.get(project_name, None)
    if(project_issues is None):
        issue.set_id(1)
        project_issues = {issue.id(): issue}
        self.project_indexes[project_name] = project_issues
        self.current_issue_ids[project_name] = issue.id()
    else:
        self.current_issue_ids[project_name] = self.current_issue_ids[project_name] + 1
        issue.set_id(self.current_issue_ids[project_name])
        project_issues[issue.id()] = issue
    
    issue_id = issue.id()
    issue.set_project_name(project_name)
    issue.set_summary(summary)
    issue.set_summary_is_escaped(False)
    issue.set_status(status)
    if owner_id != framework.constants.NO_USER_SPECIFIED:
      issue.set_owner_id(owner_id)
    issue.cc_ids_list().extend(cc_ids)
    issue.labels_list().extend(labels)
    issue.set_reporter_id(reporter_id)
    issue.set_star_count(star_count)
    if not timestamp: timestamp = int(time.time())
    issue.set_opened_timestamp(timestamp)
    issue.set_modified_timestamp(timestamp)
    
    modified_timestamps_records = self.issue_modified_timestamps.get(project_name, {})
    modified_timestamps_records[issue_id] = timestamp
    self.issue_modified_timestamps[project_name] = modified_timestamps_records

    #issue.set_id(self._MakeNextIssueId(project_name, demetrius_persist))
    comment = self._CreateIssueComment(
       project_name, issue.id(), reporter_id, marked_description,
       attachments=attachments, timestamp=timestamp, was_escaped=True)

    self._StoreIssueComment(comment)
    self._StoreIssue(issue, config)  # store issue metadata last as "keystone"


    if index_now:
      self.IndexIssueInLockedProject(project, issue, conn_pool)

    return issue_id

  def UpdateIssueInLockedProject(
    self, project, issue_id, summary, status, owner_id, cc_ids, labels,
    conn_pool, index_now=True, page_gen_ts=None):
    """Update the issue and return a set of update tuples.

    Args:
      project: the Project BO for the current project.
      issue_id: integer id of the issue to update.
      summary: new issue summary string.
      status: new issue status string.
      owner_id: user id of the new issue owner.
      cc_ids: list of user ids of users to CC when the issue changes.
      labels: list of new issue label strings.
      conn_pool: ConnectionPool object that interfaces to AuthSub.
      index_now: True if the issue should be updated in search engine.
      page_gen_ts: time at which the issue HTML page was generated,
                   used in detecting mid-air collisions.

    Returns: [(field_id, new_value), ...]
      A list of tuples that describe the set of metadata updates that
      the user made.  This tuple is later used in making the IssueComment.
    """

    status = post.CanonicalizeLabel(status)
    labels = [post.CanonicalizeLabel(l) for l in labels]

    # Get the issue and remember its current/old BT key
    project_name = project.project_name()
    config = self.GetProjectConfig(project_name)
    issue, ts = self.GetIssue(project_name, issue_id)
    #old_key = self._KeyForIssue(issue, config)

    # Store each updated value in the issue PB, and compute update_tuples
    update_tuples = []

    if summary and summary != issue.summary():
      update_tuples.append((dit_pb.IssueComment_Updates.SUMMARY, summary))
      issue.set_summary(summary)
      issue.set_summary_is_escaped(False)

    if status != issue.status():
      _UpdateClosedTimestamp(config, issue, status)
      update_tuples.append((dit_pb.IssueComment_Updates.STATUS, status))
      issue.set_status(status)

    if owner_id != issue.owner_id():
      new_owner = self.demetrius_persist.GetUser(owner_id)
      email = new_owner.account_email()
      if '@' in email:
          username, user_domain = email.split('@')
      else:
          username, user_domain = email, ''
      is_gmail_address = user_domain in ['gmail.com', 'googlemail.com']
      if is_gmail_address:
            print 
            display_name = username
      else:
            display_name = email
      update_tuples.append((dit_pb.IssueComment_Updates.OWNER,
                            display_name))
      if owner_id == framework.constants.NO_USER_SPECIFIED:
        issue.clear_owner_id()
      else:
        issue.set_owner_id(owner_id)
    cc_added = [cc for cc in cc_ids if cc not in issue.cc_ids_list()]
    cc_removed = [cc for cc in issue.cc_ids_list() if cc not in cc_ids]
    if cc_added or cc_removed:
      users_removed = []
      users_added = []
      for uid in cc_removed:
        new_owner = self.demetrius_persist.GetUser(uid)
        email = new_owner.account_email()
        if '@' in email:
          username, user_domain = email.split('@')
        else:
          username, user_domain = email, ''
        is_gmail_address = user_domain in ['gmail.com', 'googlemail.com']
        if is_gmail_address:
          display_name = username
        else:
          display_name = email
        users_removed.append('-%s' % display_name)
      for uid in cc_added:
        new_owner = self.demetrius_persist.GetUser(uid)
        email = new_owner.account_email()
        if '@' in email:
          username, user_domain = email.split('@')
        else:
          username, user_domain = email, ''
        is_gmail_address = user_domain in ['gmail.com', 'googlemail.com']
        if is_gmail_address:
          display_name = username
        else:
          display_name = email
        users_added.append('+%s' % display_name)
      update_str = ' '.join(users_removed + users_added)
      update_tuples.append((dit_pb.IssueComment_Updates.CC, update_str))
      issue.clear_cc_ids()
      issue.cc_ids_list().extend(cc_ids)
    labels_added = [lab for lab in labels
                    if lab not in issue.labels_list()]
    labels_removed = [lab for lab in issue.labels_list()
                      if lab not in labels]
    if labels_added or labels_removed:
      labels_removed = ['-%s' % lab for lab in labels_removed]
      labels_added = ['%s' % lab for lab in labels_added]
      update_str = ' '.join(labels_removed + labels_added)
      update_tuples.append((dit_pb.IssueComment_Updates.LABELS,
                            update_str))
      issue.clear_labels()
      issue.labels_list().extend(labels)

    # Raise an exeption if the issue was changed by another user
    # while this user was viewing/editing the issue.
    if page_gen_ts and len(update_tuples) > 0:
      if ts > page_gen_ts:
        log.msg('%d > %d' % (ts, page_gen_ts))
        log.msg('update_tuples: %s' % update_tuples)
        raise framework.persist.MidAirCollision(
          'issue %d' % issue_id, 'issues/detail?id=%d' % issue_id)

    # update the modified_timestamp if the issue has been changed
    # in any material way
    if update_tuples:
      issue.set_modified_timestamp(int(time.time()))

    # Store the issue
    self._StoreIssue(issue, config)

    if index_now:
      self.IndexIssueInLockedProject(project, issue, conn_pool)

    return update_tuples

  def _StoreIssue(self, issue, config, ts=None):
    """Save the given issue to disk. Assign it an ID if needed."""
    #save_to_working_copy(issue.project_name(), 'issue', issue.id(), issue)
    # TODO(students): reimplement this.

  def GetCurrentIssueId(self, project_name, demetrius_persist):
    """Return the next available issue id in this project."""
    project_issue_id = self.current_issue_ids.get(project_name, None)
    if project_issue_id is None:
        project_issue_id = 0
        self.current_issue_ids[project_name] = project_issue_id
        
    return project_issue_id
    
  def _MakeNextIssueId(self, project_name, demetrius_persist):
    """Atomically increment the next available issue id in this project."""
    project_issue_id = self.current_issue_ids.get(project_name, None)
    if project_issue_id is None:
        project_issue_id = 0
    else:
        project_issue_id = project_issue_id + 1
        
    self.current_issue_ids[project_name] = project_issue_id
    return project_issue_id

  ### IssueComments

  def GetCommentsForIssue(self, issue):
    """Return all IssueComment PBs for the given issue.

    Args:
      issue: an Issue business object.

    Returns: a list of the IssueComment business object for the description
      and comments on this issue.
    """

    return self.GetCommentsForIssueId(issue.project_name(), issue.id())

  def GetCommentsForIssueId(self, project_name, issue_id):
    """Return all IssueComment PBs for the given issue.

    Args:
      project_name: string name of the current project.
      issue_id: int issue id of the current issue.

    Returns: a list of the IssueComment business objects for the description
      and comments on this issue.
    """

    project_issue_comments = self.issue_comments.get(project_name, None)
    
    if project_issue_comments is None:
        project_issue_comments = {}
        self.issue_comments[project_name] = project_issue_comments
    
    return project_issue_comments.get(issue_id, [])

  def _StoreIssueComment(self, iss_cmnt):
    """Add a Comment PB to an issue in a locked project."""
    
    project_name = iss_cmnt.project_name()
    issue_id = iss_cmnt.issue_id()
    project_issue_comments = self.issue_comments.get(project_name, None)
    
    if project_issue_comments is None:
        project_issue_comments = {}
        issue_comment_list = []
    else:
        issue_comment_list = project_issue_comments.get(issue_id, [])
    iss_cmnt.set_comment_id(len(issue_comment_list))
    issue_comment_list.append(iss_cmnt)
    project_issue_comments[issue_id] = issue_comment_list
    self.issue_comments[project_name] = project_issue_comments

    #local_persist.save_to_working_copy(iss_cmnt.project_name(), 'issue_comment', iss_cmnt.comment_id(), iss_cmnt)
    # TODO(students): reimplement this.

  def SoftDeleteComment(self, project_name, issue_id, sequence_num,
                        deleted_by_user_id, delete=True):
    """Mark comment as un/deleted, which shows/hides it from average users."""
    all_comments = self.GetCommentsForIssueId(project_name, issue_id)
    try:
      iss_cmnt = all_comments[sequence_num]
    except IndexError:
      log.msg('Warning: Tried to delete non-existent comment #%s in project %s'
                      ' issue %s' % (sequence_num, project_name, issue_id))
      return
    if delete:
      iss_cmnt.set_deleted_by(deleted_by_user_id)
    else:
      iss_cmnt.clear_deleted_by()

    transaction = None  # TODO: reimplement
    #artifactpersist.UpdateComment(
    #  transaction, iss_cmnt, column=self.ISSUECOMMENT_COLUMN)

  def CreateIssueCommentInLockedProject(
    self, project, issue_id, user_id, content, conn_pool,
    update_tuples=None, attachments=None, index_now=True,
    timestamp=None):
    """Create and store a new comment on the specified issue.

    Args:
      project: the current Project business objects (must be locked).
      issue_id: the issue on which to add the comment.
      user_id: the user id of the user who entered the comment.
      content: string body of the comment.
      conn_pool: ConnectionPool object that interfaces to AuthSub.
      update_tuples: list of (field_id, new_value) describing the
                     metadata changes that the user made along w/ comment.
      attachments: [(filename, contents),...] attachments uploaded at
                   the time the comment was made.
      index_now: True if the issue should be updated in search engine.
      timestamp: time at which the comment was made, defaults to now.

    Returns: the new IssueComment business object.

    Note that we assume that the content is safe to echo out
    again. The content may have some markup done during input
    processing.
    """

    comment = self._CreateIssueComment(
      project.project_name(), issue_id, user_id, content,
      update_tuples=update_tuples,
      attachments=attachments, timestamp=timestamp)
    self._StoreIssueComment(comment)

    if index_now:
      issue, ts = self.GetIssue(project.project_name(), issue_id)
      self.IndexIssueInLockedProject(project, issue, conn_pool)

    return comment

  def _CreateIssueComment(
    self, project_name, issue_id, user_id, content,
    update_tuples=None, attachments=None, timestamp=None,
    was_escaped=False):
    """Create in IssueComment business object in RAM.

    Args:
      project_name: Project with the issue.
      issue_id: the issue on which to add the comment.
      user_id: the user id of the user who entered the comment.
      content: string body of the comment.
      update_tuples: list of (field_id, new_value) describing the
                     metadata changes that the user made along w/ comment.
      attachments: [(filename, contents),...] attachments uploaded at
                   the time the comment was made.
      timestamp: time at which the comment was made, defaults to now.
      was_escaped: True if the comment was HTML escaped already.

    Returns: the new IssueComment business object.

    Note that we assume that the content is safe to echo out
    again. The content may have some markup done during input
    processing.

    Any attachments are immeditately stored to disk.
    """

    comment = dit_pb.IssueComment()
    comment.set_project_name(project_name)
    comment.set_issue_id(issue_id)
    comment.set_user_id(user_id)
    comment.set_content(content)
    comment.set_was_escaped(was_escaped)
    if not timestamp: timestamp = int(time.time())
    comment.set_timestamp(int(timestamp))

    if update_tuples:
      for field, val in update_tuples:
        update_pb = dit_pb.IssueComment_Updates()
        update_pb.set_field(field)
        update_pb.set_newvalue(val)
        comment.updates_list().append(update_pb)

    if attachments:
      for filename, body in attachments:
        attach_content = self._CreateIssueAttachmentContent(project_name, body)
        self._StoreIssueAttachmentContent(attach_content)
        attach = dit_pb.IssueComment_Attachments()
        attach.set_attachment_id(attach_content.id())
        attach.set_filename(filename)
        attach.set_filesize(len(body))
        comment.attachments_list().append(attach)

    return comment


  ### Stars

  def GetIssueUserStars(self, project_name, issue_id):
    """Return the specified IssueUserStars business object.

    Args:
      project_name: the name of the current project.
      issue_id: integer issue id within that project.

    Returns: an IssueUserStars business object that lists all the
    user ids of users that have starred the specified issue.
    """

    project_ius = self.issue_user_stars.get(project_name, None)
    
    if project_ius is None:
        issueuserstars = None
        project_ius = {}
    else:
        issueuserstars = project_ius.get(issue_id, None)

    if issueuserstars is None:
      # No one starred this issue. Make a BO that has an empty list.
      issueuserstars = dit_pb.IssueUserStars()
      issueuserstars.set_issue_id(issue_id)
      issueuserstars.set_project_name(project_name)
      project_ius[issue_id] = issueuserstars
      self.issue_user_stars[project_name] = project_ius

    return issueuserstars

  def GetUserIssueStars(self, project_name, user_id):
    """Return the specified UserIssueStars business object.

    Args:
      project_name: the name of the current project.
      user_id: user id of the logged in user.

    Returns: a UserIssueStars business object that lists all the
    issue ids in the current project that have starred by the user.
    """
    project_uis = self.user_issue_stars.get(project_name, None)
    
    if project_uis is None:
        userissuestars = None
        project_uis = {}
    else:
        userissuestars = project_uis.get(user_id, None)

    if userissuestars is None:
      # No one starred this issue. Make a BO that has an empty list.
      userissuestars = dit_pb.UserIssueStars()
      userissuestars.set_user_id(user_id)
      userissuestars.set_project_name(project_name)
      project_uis[user_id] = userissuestars
      self.user_issue_stars[project_name] = project_uis

    return userissuestars

  def SetStarInLockedProject(self, project, issue_id, user_id, starred,
                             conn_pool, index_now=True):
    """Update the UserIssueStars for the given user in the given project.

    Args:
      project: the current project (must be locked).
      issue_id: integer id of an issue within that project.
      user_id: user id of the user who starred the issue.
      starred: boolean True for adding a star, False when removing one.
      conn_pool: ConnectionPool object that interfaces to AuthSub.
      index_now: True if the issue should be updated in search engine.
    """

    log.msg('SetStar:%s, %06d, %s, %s' %
                 (project.project_name(), issue_id, user_id, starred))
    issueuserstars = self.GetIssueUserStars(project.project_name(), issue_id)
    user_ids = issueuserstars.user_ids_list()
    if starred and user_id not in user_ids:
      user_ids.append(user_id)
    elif not starred and user_id in user_ids:
      user_ids.remove(user_id)
    self._StoreIssueUserStars(project.project_name(), issue_id, issueuserstars)

    delta = 0
    userissuestars = self.GetUserIssueStars(project.project_name(), user_id)
    issue_ids = userissuestars.issue_ids_list()
    if starred and issue_id not in issue_ids:
      issue_ids.append(issue_id)
      delta = 1
    elif not starred and issue_id in issue_ids:
      issue_ids.remove(issue_id)
      delta = -1
    self._StoreUserIssueStars(project.project_name(), user_id, userissuestars)

    issue, ts = self.GetIssue(project.project_name(), issue_id)
    issue.set_star_count(issue.star_count() + delta)
    config = self.GetProjectConfig(project.project_name())
    self._StoreIssue(issue, config, issue.modified_timestamp())  # Stars do not change timestamp.
    if index_now:
      self.IndexIssueInLockedProject(project, issue, conn_pool)

  def IsStarredBy(self, project_name, issue_id, user_id):
    """Return True if the given issue is starred by the given user."""
    userissuestars = self.GetUserIssueStars(project_name, user_id)
    result = issue_id in userissuestars.issue_ids_list()
    return result

  def _StoreIssueUserStars(self, project_name, issue_id, issueuserstars):
    """Store a IssueUserStars BO to disk."""
    project_ius = self.issue_user_stars.get(project_name, None)
    if project_ius is None:
        project_ius = {}

    project_ius[issue_id] = issueuserstars
    self.issue_user_stars[project_name] = project_ius
    #local_persist.save_to_working_copy(issueuserstars.project_name(), 'issue_user_stars', issueuserstars.issue_id(), issueuserstars)
    # TODO(students): reimplement this.


  def _StoreIssueUserStars(self, project_name, issue_id, issueuserstars):
    """Store a IssueUserStars BO to disk."""
    
    project_ius = self.issue_user_stars.get(project_name, None)
    if project_ius is None:
        project_ius = {}

    project_ius[issue_id] = issueuserstars
    self.issue_user_stars[project_name] = project_ius

    #local_persist.save_to_working_copy(issueuserstars.project_name(), 'issue_user_stars', issueuserstars.issue_id(), issueuserstars)
    # TODO(students): reimplement this.


  def _StoreUserIssueStars(self, project_name, user_id, userissuestars):
    """Store a UserIssueStars BO to disk."""
    project_uis = self.user_issue_stars.get(project_name, None)
    if project_uis is None:
        project_uis = {}

    project_uis[user_id] = userissuestars
    self.user_issue_stars[project_name] = project_uis
    #local_persist.save_to_working_copy(userissuestars.project_name(), 'user_issue_stars',userissuestars.user_id(), userissuestars)
    # TODO(students): reimplement this.


  ### Attachments

  def _CreateIssueAttachmentContent(self, project_name, content):
    """Create a new IssueAttachmentContent object."""
    attach_content = dit_pb.IssueAttachmentContent()
    attach_content.set_project_name(project_name)
    attach_content.set_content(content)
    attach_content.set_id(self._MakeNextAttachmentId(project_name))
    return attach_content

  def GetIssueAttachmentContent(self, project_name, attach_id):
    """Load a IssueAttachmentContent from BT.

    Args:
      project_name: the name of the current project.
      attach_id: long integer unique id of desired issue attachment.

    Returns: an IssueAttachmentContent business object that contains
    the content of the attached file.
    """
    issue_attach = None
    # TODO(students): reimplement this.
    return issue_attach

  def _MakeNextAttachmentId(self, project_name):
    """Return the next available attachment id in this project."""
    # TODO(students): reimplement this.


  ### Project configuration

  def GetProjectConfig(self, project_name):
    """Load a ProjectIssueConfig for the specified project from BT.

    Args:
      project_name: the name of the current project.

    Returns: A ProjectIssueConfig describing how this the issue tracker
    in the specified project is configured.  Projects only have a stored
    ProjectIssueConfig if a project owner has edited the configuration.
    Other projects use a default configuration.
    """

    assert project_name.lower() == project_name
    #key = self._KeyForProjectIssueConfigByName(project_name)
    #TODO: 
    config = None # TODO: repimplement.

    if config is None:
      # This project had no stored config, use the default.
      config = self._MakeDefaultProjectIssueConfig()
      config.set_project_name(project_name)

    return config

  def CreateProjectConfig(self, project_name, canned_queries=None,
                          well_known_statuses=None, well_known_labels=None,
                          excl_label_prefixes=None, well_known_prompts=None):
    """Create and store a new ProjectIssueConfig object with given info.

    Args: each argument corresponds to a field of the ProjectIssueConfig
    business object.  See comments in bo/dit.py for details.
    """

    assert project_name.lower() == project_name
    project_config = self._MakeProjectIssueConfig(
      project_name, canned_queries, well_known_statuses, well_known_labels,
      excl_label_prefixes, well_known_prompts)
    self._StoreProjectConfig(project_config)

  def UpdateConfigInLockedProject(
    self, project, conn_pool, canned_queries=None, well_known_statuses=None,
    well_known_labels=None, excl_label_prefixes=None, well_known_prompts=None,
    list_prefs=None):
    """Update project's issue tracker configuration with the given info.

    Args:
      project: the project in which to update the issue tracker config.
      conn_pool: ConnectionPool object that interfaces to AuthSub.
      canned_queries: [(query_name, user_query_fragment),...]
      open_statuses: [(status_name, docstring, means_open),...]
      well_known_labels: [(label_name, docstring),...]
      excl_label_prefixes: list of prefix strings.  Each issue should
        have only one label with each of these prefixed.
      well_known_prompts: [(prompt_name, prompt_text),...]
      list_prefs: defaults for columns and sorting.
    """
    project_name = project.project_name()
    project_config = self.GetProjectConfig(project_name)

    if canned_queries is not None:
      self._SetConfigCannedQueries(project_config, canned_queries)

    if well_known_statuses is not None:
      self._SetConfigStatuses(project_config, well_known_statuses)

    if well_known_labels is not None:
      self._SetConfigLabels(project_config, well_known_labels)

    if excl_label_prefixes is not None:
      project_config.clear_exclusive_label_prefixes()
      project_config.exclusive_label_prefixes_list().extend(
        excl_label_prefixes)

    if well_known_prompts is not None:
      self._SetConfigPrompts(project_config, well_known_prompts)

    if list_prefs:
      artifactlist.SetListPreferences(list_prefs, project_config)

    self._StoreProjectConfig(project_config)


  def _MakeProjectIssueConfig(self, project_name,
                              canned_queries, well_known_statuses,
                              well_known_labels, excl_label_prefixes,
                              well_known_prompts):
    """Return a ProjectIssueConfig with the given values."""
    if not canned_queries: canned_queries = []
    if not well_known_statuses: well_known_statuses = []
    if not well_known_labels: well_known_labels = []
    if not excl_label_prefixes: excl_label_prefixes = []
    if not well_known_prompts: well_known_prompts = []

    project_config = dit_pb.ProjectIssueConfig()
    if project_name: project_config.set_project_name(project_name)

    self._SetConfigCannedQueries(project_config, canned_queries)
    self._SetConfigStatuses(project_config, well_known_statuses)
    self._SetConfigLabels(project_config, well_known_labels)
    self._SetConfigPrompts(project_config, well_known_prompts)

    project_config.clear_exclusive_label_prefixes()
    project_config.exclusive_label_prefixes_list().extend(excl_label_prefixes)

    # TODO: hard coded for now, allow more options later.
    project_config.set_default_prompt_for_users(0)
    project_config.set_default_prompt_for_developers(1)

    return project_config

  def _SetConfigCannedQueries(self, project_config, canned_queries):
    """Internal method to set the canned queries of a ProjectIssueConfig."""
    project_config.clear_canned_queries()
    for name, se_query in canned_queries:
      cq = dit_pb.ProjectIssueConfig_Canned_queries()
      cq.set_name(name)
      cq.set_search_engine_query(se_query)
      project_config.canned_queries_list().append(cq)

  def _SetConfigStatuses(self, project_config, well_known_statuses):
    """Internal method to set the well-known statuses of ProjectIssueConfig."""
    project_config.clear_well_known_statuses()
    for status, docstring, means_open in well_known_statuses:
      wks = dit_pb.ProjectIssueConfig_Well_known_statuses()
      wks.set_status(post.CanonicalizeLabel(status))
      wks.set_status_docstring(docstring)
      wks.set_means_open(means_open)
      project_config.well_known_statuses_list().append(wks)

  def _SetConfigLabels(self, project_config, well_known_labels):
    """Internal method to set the well-known labels of a ProjectIssueConfig."""
    project_config.clear_well_known_labels()
    for label, docstring in well_known_labels:
      wkl = dit_pb.ProjectIssueConfig_Well_known_labels()
      wkl.set_label(post.CanonicalizeLabel(label))
      wkl.set_label_docstring(docstring)
      project_config.well_known_labels_list().append(wkl)

  def _SetConfigPrompts(self, project_config, well_known_prompts):
    """Internal method to set the prompts of a ProjectIssueConfig."""
    project_config.clear_well_known_prompts()
    for prompt_type, prompt_text in well_known_prompts:
      wkp = dit_pb.ProjectIssueConfig_Well_known_prompts()
      wkp.set_prompt_name(prompt_type)
      wkp.set_prompt_text(prompt_text)
      project_config.well_known_prompts_list().append(wkp)

  def _MakeDefaultProjectIssueConfig(self):
    """Return a ProjectIssueConfig with use by projects that don't have one."""
    return self._MakeProjectIssueConfig(
      None, dit.constants.DEFAULT_CANNED_QUERIES,
      dit.constants.DEFAULT_WELL_KNOWN_STATUSES,
      dit.constants.DEFAULT_WELL_KNOWN_LABELS,
      dit.constants.DEFAULT_EXCL_LABEL_PREFIXES,
      dit.constants.DEFAULT_WELL_KNOWN_PROMPTS)

  def _StoreProjectConfig(self, project_config):
    """Store the given ProjectIssueConfig BO in BT."""
    # TODO(students): reimplement this.

  ### Search and Indexing functions

  def SearchProjectCan(self, query, project_name, canned_query,
                       logged_in_user_proxy, req_info):
    """Return a list of issue ids in the project that satisfy the query.

    Args:
      user_query: string of user query in user syntax.
      project_name: the name of the project to search in.
      canned_query: string of canned query context in user syntax.
      logged_in_user_proxy: Null when no user is logged in, otherwise
        a UserIDProxy for the logged in user.
      req_info: commonly used info parsed from the request.

    Returns: a list of issue ids within the project that satisfy the query.
    """
    return self.issue_index.SearchProjectCan(query, project_name, canned_query,
                                             logged_in_user_proxy, req_info)

  def IndexIssueInLockedProject(self, project, issue, conn_pool):
    """Gather the details of an issue and send them to the indexer.

    Args:
      project: Project business object for the current project.
      issue: Issue business object for the issue to be indexed.
      conn_pool: ConnectionPool object that interfaces to AuthSub.
    """

    summary = issue.summary()
    owner_name = framework.constants.NO_USER_NAME
    if issue.owner_id():
      #owner_name = conn_pool.GetUserEmail(issue.owner_id())
      owner = self.demetrius_persist.GetUser(issue.owner_id())
      owner_name = owner.account_email()
    #reporter_name = conn_pool.GetUserEmail(issue.reporter_id())
    reporter = self.demetrius_persist.GetUser(issue.reporter_id())
    reporter_name = reporter.account_email()
    cc_names = [self.demetrius_persist.GetUser(user_id).account_email()
                for user_id in issue.cc_ids_list()]

    star_count = issue.star_count()
    issueuserstars = self.GetIssueUserStars(project.project_name(), issue.id())

    status = issue.status()
    config = self.GetProjectConfig(project.project_name())
    means_open = MeansOpenInProject(status, config)
    label_names = issue.labels_list()
    issue_comments = self.GetCommentsForIssue(issue)

    if issue_comments:
      description = issue_comments[0].content()
      commentor_names = [user.GetUsername(ic.user_id(), conn_pool)
                        for ic in issue_comments[1:]]
      comment_contents = [ic.content() for ic in issue_comments[1:]]
    else:
      description = ''
      commentor_names = []
      comment_contents = []

    #self.issue_index.WriteIssue(project, issue.id(), summary, owner_name,
    #                            reporter_name, cc_names,
    #                            issueuserstars.user_ids_list(), status,
    #                            means_open, label_names, description,
    #                            commentor_names, comment_contents)



def MeansOpenInProject(status, config):
  """Return true if this status means that the issue is still open.

  Args:
    status: issue status string. E.g., 'New'.
    config: the project_config of the current project.

  Returns: boolean True if the status means that the issue is open.
  """

  status_lower = status.lower()

  # iterate over the list of known statuses for this project
  # return true if we find a match that declares itself to be open
  for wks in config.well_known_statuses_list():
    if wks.status().lower() == status_lower:
      return wks.means_open()

  # if we didn't find a matching status we consider the status open
  return True


def _UpdateClosedTimestamp(config, issue, status):
  """Sets or unsets the closed_timestamp based based on status changes.

  If the status is changing from open to closed, the closed_timestamp is set to
  the current time.

  If the status is changing form closed to open, the close_timestamp is unset.

  If the status is changing from one closed to another closed, or from one
  open to another open, no operations are performed.

  Args:
    config: the project issue tracker configuration
    issue: the Issue business object being updated
    status: the new issue status string. E.g., 'New'
  """

  # open -> closed
  if (MeansOpenInProject(issue.status(), config)
      and not MeansOpenInProject(status, config)):

    log.msg('setting closed_timestamp on issue: %d' % issue.id())

    issue.set_closed_timestamp(int(time.time()))
    return

  # closed -> open
  if (not MeansOpenInProject(issue.status(), config)
      and MeansOpenInProject(status, config)):

    log.msg('clearing closed_timestamp on issue: %s' % issue.id())

    issue.clear_closed_timestamp()
    return
