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

"""A set of functions that provide persistence for Demetrius project hosting.

This module provides functions to get, update, create, and (in some
cases) delete each type of Demetrius business object.  It provides a logical
persistence layer on top of our storage format.

Business objects are described in bo/demetrius.py.
"""

import sys
import os
import time
import re
import threading
import random
import hashlib

from twisted.python import log
from twisted.internet import defer

from common import post
#from common import pywrapcodesitebase

from bo import demetrius_pb

import framework.helpers
import framework.persist
import framework.constants
import framework.local_persist

from demetrius import constants
from framework import user
from demetrius import projectindex
from demetrius import helpers

# import dwiki.cache
# import dwiki.wikiparser
# import dwiki.wikiformatter


class DemetriusPersist(object):
  """The persistence layer for all of Demeterius's data."""

  def __init__(self, dwiki_cache):
    """Initialize this module so that it is ready to use."""
    framework.local_persist.init(self)
    self.project_index = projectindex.ProjectIndex()
    self.users = []
    self.projects = []
    self.PROJECT_ID_COUNTER = "projectidcounter"

  ### Users

  def CreateUser(self, email, username, pwdhash, require_validation=False):
    """Create a user's account, either in the code directly or by using the 
    registration form. If you supply a 4th argument as True, the user will need
    to verify the account by visiting the account validation page and entering
    data that is supplied to the user by email. The default for require_validation
    is False, to enable easy creation of users in the code."""

    """An easy way to turn off validation (developer tool)"""
    
    USE_VALIDATION = False    
    
    """generate the user's business object, and generate
    the validation key from the timestamp of the form transaction."""
    
    user = self._MakeNewUser(email, username, pwdhash)
    sha1 = hashlib.sha1()
    sha1.update(str(time.time()))
    user.set_validation_key(str(sha1.hexdigest()))

    
    """set the user's account to require validation, if require_validation
    is true. users cannot create projects or contribute to existing projects
    if their account is not validated, although they _can_ be added to the
    membership of an existing project by a project owner. they will still not be
    able to submit/change issues or other project artifacts."""
    
    if require_validation and USE_VALIDATION:
        user.set_is_validated(0)
        # TODO: Use Twisted's email tools to email the user with a link to the
        # validation form for their account and the appropriate key to enter
        print 'new user registration'
        print 'email address: ' + str(email)
        print 'validation key: ' + str(sha1.hexdigest())

    else:
        user.set_is_validated(1)
        
    """keep the user's business object in memory and on disk."""
    self.users.append(user)
    self._StoreUser(user)
    
    
  def ValidateNewUserKey(self, email, validate_key):
    """Check to see if the key entered for the account that uses this 
    e-mail address matches the key stored in the account business object.
    if so, mark the business object as validated and re-store it.
    return a status report that the page calling this function
    can deal with in an appropriate manner."""
    
    if self.CheckIfEmailAddressIsTaken(email) is not None:
        user_id = self.LookupUserIdByEmail(email)
        user_pb = self.GetUser(user_id)
        if validate_key == user_pb.validation_key():
            user_pb.set_is_validated(1)
            # TODO: email the user with a confirmation of validation
            #self._StoreUser(user)
            return 'validated'
        else:
            return 'invalid key'
    else:
        return 'not a valid user'

  def GetUser(self, user_id):
    """Load the specified User business object."""
    user_pb = None
    if user_id is None:
        return None
    try:
        user_pb = self.users[int(user_id)]
        return user_pb
    except:
        return None

  def LookupUserIdByUsername(self, username):
    """Return the user id that corresponds to the given username."""
    id = None
    for i in range(0, len(self.users)):
        if(self.users[i].account_username() == username):
            id = i
    return id
    

  def LookupUserIdByEmail(self, email):
    """Return the user id that corresponds to the given username."""
    for i in range(0, len(self.users)):
        if(self.users[i].account_email() == email):
            return i
    #raise framework.helpers.NoSuchUserException()

  def CheckIfEmailAddressIsTaken(self, email):
    user_id = None
    for i in range(0, len(self.users)):
        if(self.users[i].account_email() == email):
            user_id = i
    return user_id


  def AddProjectOwner(self, user_id, project_name, conn_pool):
    """Add an owner to this project and update both Project and User BOs."""
    self.LockProject(project_name)
    try:
      project = self.GetProject(project_name)
      owner_ids = project.owner_ids_list()
      if user_id not in owner_ids:
        owner_ids.append(user_id)
        self.UpdateLockedProject(project_name, conn_pool, owner_ids=owner_ids)

        # write out the xml for the modified project and user
        self._StoreProject(project)
        self._StoreUser(self.GetUser(user_id))
    finally:
      self.UnlockProject(project_name)

  def RemoveProjectOwner(self, user_id, project_name, conn_pool):
    """Remove an owner from project and update both Project and User BOs."""
    self.LockProject(project_name)
    try:
      project = self.GetProject(project_name)
      owner_ids = project.owner_ids_list()
      if user_id in owner_ids:
        owner_ids = [uid for uid in owner_ids if uid != user_id]
        self.UpdateLockedProject(project_name, conn_pool, owner_ids=owner_ids)

        # write out the xml for the modified project and user
        self._StoreProject(project)
        self._StoreUser(self.GetUser(user_id))
    finally:
      self.UnlockProject(project_name)

  def AddProjectMember(self, user_id, project_name, conn_pool):
    """Add a member to this project and update both Project and User BOs."""
    self.LockProject(project_name)
    try:
      project = self.GetProject(project_name)
      member_ids = project.member_ids_list()
      if user_id not in member_ids:
        member_ids.append(user_id)
        self.UpdateLockedProject(project_name, conn_pool, member_ids=member_ids)

        # write xml
        self._StoreProject(project)
        self._StoreUser(self.GetUser(user_id))
    finally:
      self.UnlockProject(project_name)

  def RemoveProjectMember(self, user_id, project_name, conn_pool):
    """Remove a member from project and update both Project and User BOs."""
    self.LockProject(project_name)
    try:
      project = self.GetProject(project_name)
      member_ids = project.member_ids_list()
      if user_id in member_ids:
        member_ids = [uid for uid in member_ids if uid != user_id]
        self.UpdateLockedProject(project_name, conn_pool, member_ids=member_ids)

        # write xml
        self._StoreProject(project)
        self._StoreUser(self.GetUser(user_id))    
    finally:
      self.UnlockProject(project_name)

  def _AddOwnerRoleInUser(self, user_pb, project_name):
    """Add a locked project to user's list of ownership roles."""
    # TODO: get the User BO.
    if user_pb is None: 
        user_pb = self._MakeNewUser()
    else:
        user_pb = self.GetUser(user_pb)
    if project_name not in user_pb.owner_of_projects_list():
      user_pb.owner_of_projects_list().append(project_name)
      return user_pb
    return None

  def _RemoveOwnerRoleInUser(self, user_pb, project_name):
    """Remove a locked project from user's ownership roles."""
    # TODO: get the User BO.
    if user_pb is None:
        return None
    else:
        user_pb = self.GetUser(user_pb)
    if project_name in user_pb.owner_of_projects_list():
      revised_projects = [name for name in user_pb.owner_of_projects_list()
                          if name != project_name]
      user_pb.clear_owner_of_projects()
      user_pb.owner_of_projects_list().extend(revised_projects)
      return user_pb
    return None

  def _AddMemberRoleInUser(self, user_pb, project_name):
    """Callback to add a locked project to user's membership roles."""
    # TODO: get the User BO.
    if user_pb is None: 
        user_pb = self._MakeNewUser()
    else:
        user_pb = self.GetUser(user_pb)
    if project_name not in user_pb.member_of_projects_list():
      user_pb.member_of_projects_list().append(project_name)
      return user_pb
    return None

  def _RemoveMemberRoleInUser(self, user_pb, project_name):
    """Remove a locked project from user's membership roles."""
    # TODO: get the User BO.
    if user_pb is None: 
        return None
    else:
        user_pb = self.GetUser(user_pb)
    if project_name in user_pb.member_of_projects_list():
      revised_projects = [name for name in user_pb.member_of_projects_list()
                          if name != project_name]
      user_pb.clear_member_of_projects()
      user_pb.member_of_projects_list().extend(revised_projects)
      return user_pb
    return None

  def _MakeNewUser(self, email, username, pwdhash):
    """Create a new user record in RAM."""
    user_pb = demetrius_pb.User()
    user_pb.set_account_username(username)
    user_pb.set_account_password(pwdhash)
    user_pb.set_account_email(email)
    user_pb.set_is_site_admin(0)
    user_pb.set_svn_password(user.GenerateSVNPassword())
    return user_pb

  ### Projects

  def GetProject(self, project_name, fresh=False):
    """Load the specified project from memory, 
    or if it is not found, from disk.
    If fresh=True, always load it from disk."""
    
    project = None
    
    if not fresh:
        # first look for it in memory
        for i in range(0, len(self.projects)):
            if(self.projects[i].project_name() == project_name):
                project = self.projects[i]
            
    # if it wasn't in memory, try to load it from xml
    if project == None:
        
        project = framework.local_persist.load_item_from_working_copy(
            framework.local_persist.OBJECT_TYPES.PROJECT,
            project_name,
            project_name,
            True)
            
        
        if project == None:
            # project wasn't in a working copy, look for it in the unversioned directory
            project = framework.local_persist.load_item_from_working_copy(
                framework.local_persist.OBJECT_TYPES.PROJECT,
                project_name,
                project_name,
                False)
            
        if not project == None:
            self.projects.append(project)
            
            project.d_setup_svn_controller()
            
            for owner in project.owner_ids_list():
                owner_bo = self.GetUser(int(owner))
                if not project.project_name() in owner_bo.owner_of_projects_list():
                    owner_bo.add_owner_of_projects(project.project_name())
            for member in project.member_ids_list():
                member_bo = self.GetUser(int(member))
                if not project.project_name() in member_bo.member_of_projects_list():
                    member_bo.add_member_of_projects(project.project_name())
            
    return project

  def CreateProject(self, project_name, owner_ids, member_ids, summary,
                    repo_url, description, labels, lic_key, conn_pool,
                    state=demetrius_pb.Project.LIVE,
                    url_links=None, group_links=None, blog_links=None,
                    canned_issue_query_links=None, worktable=None):
    print 'creating project named', project_name
      
    """Create and store a Project with the given attributes.

    Args:
      project_name: a valid project name, all lower case.
      owner_ids: a list of user ids for the project owners.
      member_ids: a list of user ids for the project members.
      summary: one-line explanation of the project.
      repo_url: a link to the project's code repository
      description: one-page explanation of the project.
      labels: list of strings for project labels on this project.
      lic_key: a short string key for a license defined in licenses.py.
      state: a project state enum defined in bo/demetrius.py.
      url_links: list of 2-tuples with the link label and URL.
      group_links: list of 2-tuples with the label and Google Group name.
      blog_links: list of 3-tuples with the blog label, URL, and feed URL.
      canned_issue_query_links: list of 1-tuples with the canned query name.
      worktable:  needed to tell cwt to create a subversion repository.
    """
    assert self.IsValidProjectName(project_name)
    self.LockProject(project_name)
    try:
      old_project = self.GetProject(project_name)
      if old_project:
        raise ProjectAlreadyExists()

      project = demetrius_pb.Project()
      project.set_project_num(self._MakeNextProjectId())
      project.set_state(state)
      project.set_project_name(project_name)
      project.set_repository_url(repo_url)
      project.owner_ids_list().extend(owner_ids)
      for new_owner_id in owner_ids:
        self._AddOwnerRoleInUser(new_owner_id, project_name)
      project.member_ids_list().extend(member_ids)
      for new_member_id in member_ids:
        self._AddMemberRoleInUser(new_member_id, project_name)
      project.set_description(description)
      project.set_summary(summary)
      self._SetAllProjectLinks(project, url_links, group_links, blog_links,
                               canned_issue_query_links)
      project.set_license_key(lic_key)
      project.labels_list().extend(labels)

      # store the project both in memory and on the disk
      self.projects.append(project)
      self._StoreProject(project)

    finally:
      self.UnlockProject(project_name)

  def GetAllProjects(self):
    """
    Load all the Project BOs from disk
    Returns: a list of the corresponding Project business objects.
    """
    
    projects = []
    project_names = []
    
    log.msg('loading projects...')
    
    # first load all version controlled projects
    
    working_copies = os.path.join(
        framework.constants.WORKING_DIR, 
        'storage', 'working_copies')
        
    for project_wc in os.listdir(working_copies):
        project = self.GetProject(project_wc, fresh=True)
        project_name = project.project_name()
        
        projects.append( self.GetProject(project_wc, fresh=True) )
        project_names.append( project_name )
        
        log.msg('\tloaded versioned project:', project_name)
        
        
    # now load any unversioned projects
    
    unversioned_projects = os.path.join( 
        framework.constants.WORKING_DIR, 
        'storage', 'unversioned' )
        
    for project_dir in os.listdir(unversioned_projects):
        
        if project_dir in project_names:
            # we just loaded this project from a working copy, don't load it again
            # TODO: we should probably delete the second copy here
            log.msg('\tnot loading duplicate project:', project_name)
        else:
            project = self.GetProject(project_dir, fresh=True)
            project_name = project.project_name()
            
            projects.append( project )
            project_names.append( project_name )
    
            log.msg('\tloaded unversioned project:', project_name)
    
    log.msg('loaded', len(projects), 'projects')
    
    return projects


  def GetAllUsers(self):
      """
      Load all user BOs from disk
      Returns: a list of the cooresponding User buisiness objects
      """
    
      log.msg('loading users...')
    
      users = framework.local_persist.load_all_users()
  
      for user in users:
          log.msg('\tloaded user:', user.account_email())
          self.users.append(user)
          
      log.msg('loaded', len(users), 'users')
 

  def GetProjectDescriptionCachedBlob(self, project_name):
      # TODO: maybe this is supposed to return a cashed version of the wikified project description?
      return "project description cashed blob for " + str(project_name)

  def UpdateLockedProject(self, project_name, conn_pool,
                          owner_ids=None, member_ids=None,
                          summary=None, description=None, labels=None,
                          license_key=None, url_links=None, group_links=None,
                          blog_links=None, canned_issue_query_links=None,
                          state=None, commit_notify=None, issue_notify=None,
                          attachment_bytes_used=None, download_bytes_used=None,
                          analytics_account=None,
                          persist_repository_url=None,
                          persist_repository_username=None,
                          persist_repository_password=None,
                          source_url=None):
    """Update the named project with any of the given information.
    Returns the updated project or, if a change needs to be done to the
    project's svn controller, returns a deferred"""
    assert self.IsValidProjectName(project_name)
    project = self.GetProject(project_name)

    if owner_ids is not None:
      new_owner_ids = [user_id for user_id in owner_ids
                       if user_id not in project.owner_ids_list()]
      for new_owner_id in new_owner_ids:
        self._AddOwnerRoleInUser(new_owner_id, project_name)
      former_owner_ids = [user_id for user_id in project.owner_ids_list()
                          if user_id not in owner_ids]
      for former_owner_id in former_owner_ids:
        self._RemoveOwnerRoleInUser(former_owner_id, project_name)
      project.clear_owner_ids()
      project.owner_ids_list().extend(owner_ids)

    if member_ids is not None:
      new_member_ids = [user_id for user_id in member_ids
                       if user_id not in project.member_ids_list()]
      for new_member_id in new_member_ids:
        self._AddMemberRoleInUser(new_member_id, project_name)
      former_member_ids = [user_id for user_id in project.member_ids_list()
                          if user_id not in member_ids]
      for former_member_id in former_member_ids:
        self._RemoveMemberRoleInUser(former_member_id, project_name)
      project.clear_member_ids()
      project.member_ids_list().extend(member_ids)

    if summary is not None:
      project.set_summary(summary)

    if description is not None and description != project.description():
      project.set_description(description)
      project.set_wikiize_description(True)

    if labels is not None:
      project.clear_labels()
      project.labels_list().extend(labels)

    self._SetAllProjectLinks(project, url_links, group_links, blog_links,
                             canned_issue_query_links)
    if license_key is not None: project.set_license_key(license_key)
    if state is not None: project.set_state(state)
    if commit_notify is not None:
      project.clear_commit_notify_address()
      if commit_notify:
        project.set_commit_notify_address(commit_notify)
    if issue_notify is not None:
      project.clear_issue_notify_address()
      if issue_notify:
        project.set_issue_notify_address(issue_notify)
    if attachment_bytes_used is not None:
      project.set_attachment_bytes_used(attachment_bytes_used)
    if download_bytes_used is not None:
      project.set_download_bytes_used(download_bytes_used)
    if analytics_account is not None:
      if analytics_account:
        project.set_analytics_account(analytics_account)
      else:
        project.clear_analytics_account()
    
    if source_url is not None:
        project.set_repository_url(source_url)
    
    self.IndexProject(project, conn_pool)
    self._StoreProject(project)
    
    # update the project's svn_controller
    
    # if there was a change to the svn_controller, 
    # this method will result in a deferred that will eventually return the project
    
    persist_changed = False
    
    if persist_repository_url is not None:
      project.set_persist_repository_url(persist_repository_url)
      persist_changed = True
    if persist_repository_username is not None:
      project.set_persist_repository_username(persist_repository_username) 
      persist_changed = True
    if persist_repository_password is not None:
      project.set_persist_repository_password(persist_repository_password)
      persist_changed = True
    
    if(persist_changed):
        def svn_exception(e):
            raise e
        def return_project(*args):
            return project
        d = project.d_setup_svn_controller()
        d.addErrback(svn_exception)
        d.addCallback(return_project)
        return d
    else:
        return project

  def DeleteProject(self, project_name,
                    new_state=demetrius_pb.Project.DELETE_PENDING,
                    reason='Project owner request', delete_time=None):
    """Mark the named project as deleted or doomed.

    Args:
      project_name: string name of the project to delete.
      new_state: integer new state for project.  Defined in bo/demetrius.py.
      reason: string human-readable reason for deletion or doom.
      delete_time: time at which project may be reaped, defaults to now.

    We never actually lose any artifacts.  The project is still visible to
    admins and project members, until it is archived by a reaper process.
    """

    assert self.IsValidProjectName(project_name)
    if delete_time is None:
      delete_time = int(time.time())
    self.LockProject(project_name)
    try:
      project = self.GetProject(project_name)
      if project:
        project.set_state(new_state)
        project.set_delete_reason(reason)
        project.set_delete_time(delete_time)
        self._StoreProject(project)
        # Note that we do not update search engine yet, because project will
        # still be shown in search results to admins only.
    finally:
      self.UnlockProject(project_name)

  def DoomProject(self, project_name, reason=constants.DEFAULT_DOOM_REASON,
                  doom_period=constants.DEFAULT_DOOM_PERIOD):
    """Mark the project as doomed to deletion unless the owner contacts us.

    Args:
      project_name: string name of the project to delete.
      reason: string human-readable reason for deletion or doom.
      doom_period: delay from now until time when project may be reaped.

    The default reason is that the project was abandoned by its owners.  The
    default delay before the project may be reaped/archived is 3 days.
    """

    self.DeleteProject(project_name, new_state=demetrius_pb.Project.DOOMED,
                       reason=reason,
                       delete_time=int(time.time()) + doom_period)

  def HideProject(self, project_name, conn_pool):
    """Update the Project PB to mark it as HIDDEN.

    Args:
      project_name: string name of the project to hide.
      conn_pool: ConnectionPool instance needed for all updates.
    """

    self.LockProject(project_name)
    try:
      self.UpdateLockedProject(project_name, conn_pool,
                               state=demetrius_pb.Project.HIDDEN)
    finally:
      self.UnlockProject(project_name)

  def PublishProject(self, project_name, conn_pool):
    """Update the project's state to make it published (i.e., state is LIVE).

    Args:
      project_name: string name of the project to publish.
      conn_pool: ConnectionPool instance needed for all updates.
    """

    self.LockProject(project_name)
    try:
      self.UpdateLockedProject(project_name, conn_pool,
                               state=demetrius_pb.Project.LIVE)
    finally:
      self.UnlockProject(project_name)

  def IsValidProjectName(self, string):
    """Return true if the given string is a valid project name."""
    return constants.RE_PROJECT_NAME.match(string)

  def _SetAllProjectLinks(self, project, url_links, group_links,
                          blog_links, canned_issue_query_links):
    """Update all the project link PBs with the given tuples."""
    if url_links is not None:
      project.clear_linksurl()
      for label, url in url_links:
        link_pb = project.add_linksurl()
        link_pb.set_label(label)
        link_pb.set_url(url)

    if group_links is not None:
      project.clear_linksgroup()
      for label, group_name in group_links:
        link_pb = project.add_linksgroup()
        link_pb.set_label(label)
        link_pb.set_group_name(group_name)

    if blog_links is not None:
      project.clear_linksblog()
      for label, url in blog_links:
        link_pb = project.add_linksblog()
        link_pb.set_label(label)
        link_pb.set_url(url)

    if canned_issue_query_links is not None:
      project.clear_linksissues()
      for query_name in can_links:
        link_pb = project.add_linksissues()
        link_pb.set_query_name(query_name)

  def _StoreProject(self, project):
    log.msg('storing project', project.project_name())
    framework.local_persist.save_to_working_copy(project.project_name(), 
                    framework.local_persist.OBJECT_TYPES.PROJECT,
                    project.project_name(), 
                    project,
                    project.has_working_copy())
    
    framework.local_persist.save_to_local_disk(
                framework.local_persist.OBJECT_TYPES.PROJECT,
                project.project_name(), 
                project)
    
    if(project.has_working_copy()):
        print 'commiting working copy'
        project.svn_controller().d_up_add_commit(
            message='project information changed')
    else:
        print 'project', project.project_name(), 'has no working copy'

  def _StoreUser(self, user):
      log.msg('storing user', user.account_username())
      framework.local_persist.save_to_local_disk(
                framework.local_persist.OBJECT_TYPES.USER,
                user.account_username(),
                user)
      
      
      
  def IndexProject(self, project, conn_pool):
    """TODO implement Send all the relevant info on a project to the search engine."""
    pass
    # all_user_ids = project.owner_ids_list() + project.member_ids_list()
    # cuis_by_id = conn_pool.GetClientUserInfoBatch(all_user_ids)
    # owners = [framework.helpers.UserIDProxy(
    #            user_id, demetrius_persist)
    #           for user_id in project.owner_ids_list()]
    # owner_names = [owner.username for owner in owners]
    # 
    # members = [framework.helpers.UserIDProxy(
    #              user_id, demetrius_persist)
    #            for user_id in project.member_ids_list()]
    # member_names = [member.username for member in members]
    # 
    # self.project_index.WriteProject(
    #   project.project_name(), project.project_num(), project.summary(),
    #   project.description(), owner_names, member_names, project.labels_list())

  def _MakeNextProjectId(self):
    """Return the next available project id for a new project.

    This cannot be a random 64bit key from the keyserver, because it must
    be a 32bit number.
    """
    return self._GetAndIncrementCounter(self.PROJECT_ID_COUNTER)

  ### Locking

  def LockProject(self, project_name):
    """Lock a project by locking a resource with a corresponding name."""
    assert self.IsValidProjectName(project_name)
    self.LockResource('project:%s' % project_name)

  def LockResource(self, resource_name):
    """Lock resource so that no other thread or frontend server can have it."""
    # TODO(students): reimplement this.
    pass

  def UnlockProject(self, project_name):
    """Unlock a project by unlocking the corresponding resource name."""
    self.UnlockResource('project:%s' % project_name)

  def UnlockResource(self, resource_name):
    """Unlock a resource by deleting the lock."""
    # TODO(students): reimplement this.
    pass

  def _GetCounter(self, counter_name):
    """Get the current value of a counter stored on disk."""
    if not os.path.isfile(counter_name+".txt"):
        open(counter_name+".txt", "w+").close
    count_file = open(counter_name+".txt", "r")
    current_count = count_file.read()
    if current_count == "":
        current_count = 0
    else:
        current_count = int(current_count)
    count_file.close
    return current_count

  def _GetAndIncrementCounter(self, counter_name, delta=1):
    """Atomically read and increment a counter stored on disk."""
    current_count = self._GetCounter(counter_name)

    count_file = open(counter_name+".txt", "w+")
    count_file.write(str(current_count + delta))
    count_file.close

    return current_count
    


class Error(Exception):
  """Base exception class for this package."""


class ProjectAlreadyExists(Error):
  """Tried to create a project that already exists."""


if __name__ == '__main__':
  sys.exit('This is not meant to be run as a standalone program. Exiting.')
