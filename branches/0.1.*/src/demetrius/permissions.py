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

"""Simple map from (user role, project status) to specific perms.

A permission is simply a string.  The servlets and templates can test
whether the current user has permission to see a UI element or perform
an action by testing for the presence of the corresponding permission.

The user role is one of admin, owner, member, gmail user, (google) user,
or anon.

The project status is one of the project states defined in bo/demetrius.py,
or a special constant defined below.
"""

from ezt import ezt

from bo import demetrius_pb

VIEW_PROJECT = 'view_project'
EDIT_PROJECT = 'edit_project'
COMMIT = 'commit'
CREATE_PROJECT = 'create_project'
PUBLISH_PROJECT = 'publish_project' # for making HIDDEN projects LIVE
APPROVE_PROJECT_NAME = 'approve_project_name' # admins can grant reserved names
VIEW_DEBUG = 'view_debug' # on-page debugging info
IGNORE_RESERVATION = 'ignore_reservation' # can ignore name reservations
EDIT_OTHER_USERS = 'edit_other_users' # can edit other user's prefs, ban, etc.

ADMIN_ROLE = 'admin'
OWNER_ROLE = 'owner'
MEMBER_ROLE = 'member'
# TODO: combine GMAIL_USER_ROLE w/ USER_ROLE to simplify.
GMAIL_USER_ROLE = 'gmail_user'
USER_ROLE = 'user'
ANON_ROLE = 'anon'

NO_PROJECT_STATUS = 'noproject'
WILDCARD_PROJECT_STATUS = 'wildcardstatus'

# Permissions to soft-delete artifact comment
DELETE_ANY = 'delete_any'
DELETE_OWN = 'delete_own'

# Permission to view private artifacts
VIEW_PRIVATE_ARTIFACT = 'view_private_artifact'

# The label that indicates that VIEW_PRIVATE_ARTIFACT is required
PRIVATE_ARTIFACT_LABEL = 'private'


class PermissionSet(object):
  """Class to represent the set of permissions available to the user.
  """

  def __init__(self, perms):
    """Create a PermissionSet with the given permissions."""
    self.perm_list = perms

  def __getattr__(self, name):
    """Easy permission testing in EZT.  E.g., [if-any perms.format_drive]."""
    return self.Check(name)

  def Check(self, name):
    """Return True if the user has the named permission, otherwise None."""
    return ezt.boolean(name in self.perm_list)

  def DebugString(self):
    """Return a useful string to show when debugging."""
    return 'PermissionSet(%s)' % ', '.join(self.perm_list)


EMPTY_PERMISSIONSET = PermissionSet([])

READ_ONLY_PERMISSIONSET = PermissionSet([VIEW_PROJECT])
OWNERS_PERMISSIONSET = PermissionSet([VIEW_PROJECT, EDIT_PROJECT, COMMIT,
                                      VIEW_PRIVATE_ARTIFACT,])
MEMBERS_PERMISSIONSET = PermissionSet([VIEW_PROJECT, COMMIT,
                                       VIEW_PRIVATE_ARTIFACT,])


# Permissions for project pages, e.g., the project summary page
_DEMETRIUS_PERMISSIONS = {

  # Admins can do anything, anywhere.  Even SECURE or LOCKED projects.
  (ADMIN_ROLE, WILDCARD_PROJECT_STATUS):
    PermissionSet([VIEW_PROJECT, EDIT_PROJECT, PUBLISH_PROJECT, VIEW_DEBUG,
                   COMMIT, VIEW_PRIVATE_ARTIFACT,]),

  # Project owners can view/edit their own project, regardless of state.
  # Note: EDIT_PROJECT is not enough permission to re-publish a DOOMED project.
  (OWNER_ROLE, demetrius_pb.Project.LIVE):
    OWNERS_PERMISSIONSET,
  (OWNER_ROLE, demetrius_pb.Project.DELETE_PENDING):
    OWNERS_PERMISSIONSET,
  (OWNER_ROLE, demetrius_pb.Project.MOVED):
    OWNERS_PERMISSIONSET,
  (OWNER_ROLE, demetrius_pb.Project.DOOMED):
    OWNERS_PERMISSIONSET,
  (OWNER_ROLE, demetrius_pb.Project.HIDDEN):
    OWNERS_PERMISSIONSET,
  (OWNER_ROLE, demetrius_pb.Project.SECURE):
    OWNERS_PERMISSIONSET,
  # Except for LOCKED state.  Not even owners have access to LOCKED.

  # Project members can view their own project, regardless of state.
  (MEMBER_ROLE, demetrius_pb.Project.LIVE):
    MEMBERS_PERMISSIONSET,
  (MEMBER_ROLE, demetrius_pb.Project.DELETE_PENDING):
    MEMBERS_PERMISSIONSET,
  (MEMBER_ROLE, demetrius_pb.Project.MOVED):
    MEMBERS_PERMISSIONSET,
  (MEMBER_ROLE, demetrius_pb.Project.DOOMED):
    MEMBERS_PERMISSIONSET,
  (MEMBER_ROLE, demetrius_pb.Project.HIDDEN):
    MEMBERS_PERMISSIONSET,
  (MEMBER_ROLE, demetrius_pb.Project.SECURE):
    MEMBERS_PERMISSIONSET,
  # Except for LOCKED state.  Not even members have access to LOCKED.

  # Non-members can only view projects in LIVE or MOVED states.
  (GMAIL_USER_ROLE, demetrius_pb.Project.LIVE):
    READ_ONLY_PERMISSIONSET,

  (GMAIL_USER_ROLE, demetrius_pb.Project.MOVED):
    READ_ONLY_PERMISSIONSET,

  (USER_ROLE, demetrius_pb.Project.LIVE):
    READ_ONLY_PERMISSIONSET,

  (USER_ROLE, demetrius_pb.Project.MOVED):
    READ_ONLY_PERMISSIONSET,

  (ANON_ROLE, demetrius_pb.Project.LIVE):
    READ_ONLY_PERMISSIONSET,

  (ANON_ROLE, demetrius_pb.Project.MOVED):
    READ_ONLY_PERMISSIONSET,

  # Permissions for site pages, e.g., creating a new project

  (ADMIN_ROLE, NO_PROJECT_STATUS):
    PermissionSet([CREATE_PROJECT, VIEW_DEBUG, APPROVE_PROJECT_NAME,
                   IGNORE_RESERVATION, EDIT_OTHER_USERS]),

  (GMAIL_USER_ROLE, NO_PROJECT_STATUS):
    PermissionSet([CREATE_PROJECT]),

  (USER_ROLE, NO_PROJECT_STATUS):
    PermissionSet([CREATE_PROJECT]),

  }


def GetPermissions(request, user_pb, user_id, verified, has_gmail, project,
                   permissions_dict=_DEMETRIUS_PERMISSIONS):
  """Return a demetrius permission set appropriate for the user and project.

  If an exact match for the user's role and project status is found, that is
  returned. Otherwise, we look for permissions for the user's role that is
  not specific to any project status.  If that is not defined either, we
  give the user an empty permission set.
  """
  key = GetPermissionKey(user_pb, user_id, verified, has_gmail, project)
  try:
    result = permissions_dict[key]
  except KeyError:
    wildcard_key = (key[0], WILDCARD_PROJECT_STATUS)
    result = permissions_dict.get(wildcard_key, EMPTY_PERMISSIONSET)

  isLocalIp = False  # TODO: reimplement. Did request come from localhost?
  # I think the following was to lock out non privilenged Google employees
  """
  if (isCorpIp and VIEW_PROJECT not in result.perm_list and
      project.state() != demetrius_pb.Project.SECURE):
      result = READ_ONLY_PERMISSIONSET
  """
  return result


def GetPermissionKey(user_pb, user_id, verified, has_gmail, project):
  """Return a permission lookup key appropriate for the user and project."""
  if user_id is None:
    role = ANON_ROLE
  elif not verified:  # unverified Google Accounts are treated as anon
    role = ANON_ROLE
  elif user_pb is None:  # this user never joined any project
    role = USER_ROLE
  elif user_pb.is_site_admin():
    role = ADMIN_ROLE
  elif project and project.project_name() in user_pb.owner_of_projects_list():
    role = OWNER_ROLE
  elif project and project.project_name() in user_pb.member_of_projects_list():
    role = MEMBER_ROLE
  else:
    role = USER_ROLE

  if role == USER_ROLE:# and has_gmail:
    role = GMAIL_USER_ROLE

  if project is None:
    status = NO_PROJECT_STATUS
  else:
    status = project.state()

  try:
      status = int(status)
  except Exception:
  	  # sometimes status is a string, not an int. this is ok
      pass

  return role, status


def UserCanViewProject(user_pb, project):
  """Return True if the user can view the given project.

  This is used to quickly check all the projects in a project
  search result set.  We do not use the PermissionSet objects
  because we only want one bit of information.
  """

  if project.state() == demetrius_pb.Project.LIVE:
    return True  # anyone can view a live project
  if project.state() == demetrius_pb.Project.MOVED:
    return True  # anyone can view a moved project
  if (project.state() == demetrius_pb.Project.LOCKED and
      (not user_pb or not user_pb.is_site_admin())):
    return False  # only admins can view a locked project

  # Projects in HIDDEN, DOOMED, DELETE_PENDING, and SECURE states can only
  # be viewed by logged in project members or admins.
  if user_pb is None:
    return False

  return (user_pb.is_site_admin() or
          project.project_name() in user_pb.owner_of_projects_list() or
          project.project_name() in user_pb.member_of_projects_list())


def CanDelete(logged_in_user_id, perms, artifact, creator_user_id=None):
  """Checks if user has permission to view/delete an artifact or comment."""
  if not logged_in_user_id or not perms:
    return False  # User has no authority.
  if perms.Check(DELETE_ANY):
    return True  # Site admin or project owners can delete any comment.
  if (artifact.has_deleted_by() and
      artifact.deleted_by() != logged_in_user_id):
    return False  # Users cannot undelete unless they deleted.
  if creator_user_id is None:
    creator_user = artifact.creator_user()
  if perms.Check(DELETE_OWN) and creator_user_id == logged_in_user_id:
    return True  # Users can delete their own items.
  return False


def CanView(logged_in_user_id, perms, artifact, creator_user_id):
  """Checks if user has permission to view an artifact."""
  if perms.Check(VIEW_PRIVATE_ARTIFACT):
    return True
  if logged_in_user_id == creator_user_id:
    return True
  for lab in artifact.labels_list():
    if lab.lower() == PRIVATE_ARTIFACT_LABEL:
      return False
  return True


class Error(Exception):
  """Base class for errors from this module."""


class PermissionException(Error):
  """The user is not authorized to make the current request."""
