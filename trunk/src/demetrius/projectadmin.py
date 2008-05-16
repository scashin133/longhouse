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

"""Page and form handlers for project administration.

Summary of classes:
  ProjectAdmin: This page allows editing of the project summary data.
  ProjectAdminMembers: This edits the project members.
  ProjectAdminAdvanced: This allows changing of the project state.
"""

import time
import re
import os

from ezt import ezt

from twisted.python import log

from common import http
from common import post
from common import validate
from common import ezt_google

import framework.helpers
import framework.constants

from bo import demetrius_pb
from demetrius import constants
from demetrius import pageclasses
from demetrius import helpers
from demetrius import permissions
from demetrius import licenses
from framework.svncontrols import SvnException

# Used to validate the Google Analytics account number.
_ANALYTICS_RE = re.compile(r'^UA-[0-9]+-[0-9]+$')

_RE_EMAIL_SEPARATORS = re.compile(r'\s|,|;')

class ProjectAdmin(pageclasses.DemetriusPage):
  """A page with project configuration options for the Project Owner(s)."""

  _PAGE_TEMPLATE = 'demetrius/project-admin-page.ezt'
  _MAIN_TAB_MODE = constants.MAIN_TAB_ADMIN

  def AssertBasePermission(self, req_info):
    pageclasses.DemetriusPage.AssertBasePermission(self, req_info)
    # TODO: i18n error messages
    if not req_info.demetrius_perms.Check(permissions.EDIT_PROJECT):
      raise permissions.PermissionException(
        'You are not allowed to administer this project')

  def GatherPageData(self, request, req_info):
    """Build up a dictionary of data values to use when rendering the page."""
    page_data = {
      'admin_tab_mode': constants.ADMIN_TAB_META,
      'errors': req_info.errors or ezt_google.EZTError(),
      'show_help': ezt.boolean(req_info.user_pb and
                               req_info.user_pb.keep_wiki_help_open()),
      'analytics_account': req_info.GetParam(
                             'analytics_account',
                             req_info.project.analytics_account()),
      }

    # add data that is common and immutable to all requests
    options = helpers.BuildProjectAdminOptions(
      req_info.project, req_info.user_pb)
    page_data.update(options)

    # if there are processing errors in ProcessForm, synthetic_params will
    # be defined with previous user supplied values
    if req_info.synthetic_params:
      page_data.update(req_info.synthetic_params)

      # serialize the labels to the format expected by the template
      labels = req_info.synthetic_params['labels']
      for i in range(15):
        value = ''
        if i < len(labels):
          value = labels[i]
        page_data['label%s' % str(i + 1)] = value

      # proxy the licenses again to provide data in a template friendly format
      page_data['project_license'] = helpers.LicenseProxy(
        req_info.project, license_key=page_data['license_key'])

    # no errors, so just scoop up the data from our storage
    else:
      meta = helpers.BuildProjectMeta(req_info.project, self.demetrius_persist)
      links = helpers.BuildProjectLinks(req_info.project)

      page_data.update(meta)
      page_data.update(links)

    post.URLCommandAttacksEncode(page_data, req_info.logged_in_user_id)
    return page_data

  def ProcessForm(self, request, req_info):
    """Process the posted form."""
    errors = ezt_google.EZTError()
    post_data = post.ProcessPOSTBody(
        request, framework.constants.MAX_POST_BODY_SIZE,
        keep_blank_values=True)
    if post_data is None:
      # An error occurred and the response was generated. We're done.
      raise framework.helpers.AlreadySentResponse()

    post.URLCommandAttacksCheck(post_data, req_info.logged_in_user_id)

    self.demetrius_persist.LockProject(req_info.project_name)
    try:
      summary, description, license_key, labels, source_url = self._ParseMeta(
         post_data, errors)

      if len(labels) > constants.MAX_PROJECT_LABELS:
        errors.labels = ('Too many labels.  The limit is %d.' %
                         constants.MAX_PROJECT_LABELS)

      url_links, group_links, blog_links = self._ParseLinks(post_data, errors)
      commit_notify, issue_notify = self._ParseNotify(post_data, errors)

      if errors.AnyErrors():
        log.msg('Errors identified during processing: %s'
            % errors.DebugString());

      if len(url_links) > constants.MAX_PROJECT_LINKS:
        errors.links = ('Too many links.  The limit is %d.' %
                        constants.MAX_PROJECT_LINKS)
      if len(group_links) > constants.MAX_PROJECT_GROUPS:
        errors.groups = ('Too many groups.  The limit is %d.' %
                        constants.MAX_PROJECT_GROUPS)
      if len(blog_links) > constants.MAX_PROJECT_BLOGS:
        errors.blogs = ('Too many blogs links.  The limit is %d.' %
                        constants.MAX_PROJECT_BLOGS)

      analytics_account = ''
      if 'analytics_account' in post_data:
        analytics_account = post_data['analytics_account'][0].strip().upper()
        if analytics_account and not _ANALYTICS_RE.match(analytics_account):
          errors.analytics_account = 'Invalid account number format'

      if not errors.AnyErrors():
        self.demetrius_persist.UpdateLockedProject(
          req_info.project_name, self.conn_pool,
          summary=summary, description=description, labels=labels,
          license_key=license_key, url_links=url_links,
          group_links=group_links, blog_links=blog_links,
          commit_notify=commit_notify, issue_notify=issue_notify,
          analytics_account=analytics_account, source_url=source_url)
        
        # write the xml and commit
        self.demetrius_persist._StoreProject(self.demetrius_persist.GetProject(req_info.project_name))

    finally:
      self.demetrius_persist.UnlockProject(req_info.project_name)

    # if we have any errors, we need bounce all of the data back to the
    # user to edit their input
    if errors.AnyErrors():

      # collect together all other known request data
      params = {
        'summary': summary,
        'description': description,
        'license_key': license_key,
        'labels': labels,
        'analytics_account': analytics_account,
      }

      # reprocess links
      params.update(helpers.BuildProjectLinks(req_info.project, url_links,
        group_links, blog_links))

      req_info.PrepareForSubrequest(req_info.project_name, errors, **params)

      self.Handler(request, req_info=req_info)
    else:
      url = framework.helpers.FormatAbsoluteURL(
        req_info, constants.ADMIN_META_PAGE_URL, request,
        saved=1, ts=int(time.time()))
      http.SendRedirect(url, request)

  def _ParseMeta(self, post_data, errors):
    """Process the project metadata section of the admin page."""
    summary = None
    description = None
    license_key = None
    source_url = None
    labels = []

    if 'summary' in post_data:
      summary = post_data['summary'][0]
      if len(summary) < 3:
        errors.summary = 'Summary too short'
    if 'description' in post_data:
      description = post_data['description'][0]
      if len(description) < 3:
        errors.description = 'Description too short'
    if 'license_key' in post_data:
      license_key = post_data['license_key'][0]
      if license_key not in licenses.ALL_LICENSES:
        errors.license_key = 'Invalid license key'
    if 'plabel' in post_data:
      labels = post_data['plabel']  # a list
    labels = [post.CanonicalizeLabel(label) for label in labels
              if label.strip()]  # Skip blanks, since post_data has blanks now.
    if 'source_url' in post_data:
        source_url = post_data['source_url'][0]
        print 'source url: ' + str(source_url)
        if len(source_url) > 0:
            if source_url.startswith(('svn://', 'svn+ssh://', 'http://', 'https://')) is False:
                errors.source_url = 'Invalid source URL. Make sure to enter a valid subversion URL (starting with either http://..., https://..., svn://..., or svn+ssh://...).'

    return summary, description, license_key, labels, source_url

  def _ParseLinks(self, post_data, errors):
    """Process the url links section of the admin page."""
    url_links = _ExtractPairs(post_data, 'linklabel', 'linkurl',
                              errors, 'links')
    group_links = _ExtractPairs(post_data, 'grouplabel', 'groupname',
                                errors, 'groups')
    blog_links = _ExtractPairs(post_data, 'bloglabel', 'blogurl',
                               errors, 'blogs')
    return url_links, group_links, blog_links

  def _ParseNotify(self, post_data, errors):
    """Process the project notification section of the admin page."""

    try:
      commit_notify = post.LoadFieldFromPOST('commit_notify', post_data,
                                             validator=validate.Email())
    except validate.InvalidFormattedField, e:
      errors.commit_notify = e.text
      commit_notify = post.LoadFieldFromPOST('commit_notify', post_data)

    try:
      issue_notify = post.LoadFieldFromPOST('issue_notify', post_data,
                                             validator=validate.Email())
    except validate.InvalidFormattedField, e:
      errors.issue_notify = e.text
      issue_notify = post.LoadFieldFromPOST('issue_notify', post_data)

    return commit_notify, issue_notify


class ProjectAdminPersist(pageclasses.DemetriusPage):
    """
    A page for configuring Longhouse's persistence layer.
    e.g. repository url, username, and password
    """
    _PAGE_TEMPLATE = 'demetrius/project-admin-persist-page.ezt'
    _MAIN_TAB_MODE = constants.MAIN_TAB_ADMIN

    def AssertBasePermission(self, req_info):
        pageclasses.DemetriusPage.AssertBasePermission(self, req_info)
        if not req_info.demetrius_perms.Check(permissions.EDIT_PROJECT):
          raise permissions.PermissionException(
            'You are not allowed to administer this project')
    
    def GatherPageData(self, request, req_info):
        """Build up a dictionary of data values to use when rendering the page."""
        page_data = {
          'admin_tab_mode': constants.ADMIN_TAB_PERSIST,
          'errors': req_info.errors or ezt_google.EZTError(),
          'post_commit_hook' : self._GetPostCommitHook(req_info)
          }

        post.URLCommandAttacksEncode(page_data, req_info.logged_in_user_id)
        return page_data
        
    def _GetPostCommitHook (self, req_info):
        return open(
            os.path.join(
                framework.constants.WORKING_DIR,
                'scripts',
                'post-commit'
            )).read()

    def ProcessForm(self, request, req_info):
        """Process the posted form."""
        errors = ezt_google.EZTError()
        post_data = post.ProcessPOSTBody(
            request, framework.constants.MAX_POST_BODY_SIZE)
        if post_data is None:
            # An error occurred and the response was generated. We're done.
            raise framework.helpers.AlreadySentResponse()

        post.URLCommandAttacksCheck(post_data, req_info.logged_in_user_id)

        self.demetrius_persist.LockProject(req_info.project_name)
        
        try:
            repository, username, password = self._ParsePersist(post_data, errors)

            if not errors.AnyErrors():
                
                print 'updating project', repository, username, password
                updated_project = self.demetrius_persist.UpdateLockedProject(
                    req_info.project_name, self.conn_pool,                                       
                    persist_repository_url=repository,
                    persist_repository_username=username,
                    persist_repository_password=password)
                    
                def finishForm(*args):
                    self._FinishProcessingForm(request, req_info, errors, repository, username, password)    
                    
                def updateProjectError(e):
                    print 'error updating locked project', e
                    print e.getTraceback()
                    errors.svn_connect = 'Could not connect to subversion repository'
                    
                # TODO: use isinstance() here instead?
                if str(updated_project.__class__) == 'twisted.internet.defer.Deferred':
                    updated_project.addErrback(updateProjectError)
                    updated_project.addCallback(finishForm)
                    return updated_project
                else:
                    finishForm()
                
        except Exception, e:
            print 'exception in ProjectAdminPersist.ProcessForm:', e
            raise


    def _FinishProcessingForm(self, request, req_info, errors, repository, username, password):
        """ All deferreds have returned, finish processing """
        
        print 'finishing processing form'
        
        self.demetrius_persist.UnlockProject(req_info.project_name)
        
        if errors.AnyErrors():

            print 'There were errors processing ProjectAdminPersist form. Preparing subrequest...'

            params = {
                'repository' : repository,
                'username' : username,
                'password' : password
                }
            
            req_info.PrepareForSubrequest(req_info.project_name, errors, **params)
            self.Handler(request, req_info=req_info)
        else:
            url = framework.helpers.FormatAbsoluteURL(
                req_info, constants.ADMIN_PERSIST_PAGE_URL, request,
                saved=1, ts=int(time.time()))
            http.SendRedirect(url, request)


    def _ParsePersist(self, post_data, errors):
        """Process the submited svn information"""
        repository = None
        username = None
        password = None
        
        if 'repository' in post_data:
            repository = post_data['repository'][0]
            if len(repository) < 5:
                errors.repository = 'Repository URL too short'
        else:
            errors.repository = 'Repository URL too short'
            
        if 'username' in post_data:
            username = post_data['username'][0]
        
        if 'password' in post_data:
            password = post_data['password'][0]
        
        return repository, username, password
        
    def HookFileHandler( self, request ):
        request.write('hello world!')
        


class ProjectAdminMembers(pageclasses.DemetriusPage):
  """A page with project configuration options for the Project Owner(s)."""

  _PAGE_TEMPLATE = 'demetrius/project-admin-members-page.ezt'
  _MAIN_TAB_MODE = constants.MAIN_TAB_ADMIN

  def AssertBasePermission(self, req_info):
    pageclasses.DemetriusPage.AssertBasePermission(self, req_info)
    # TODO: i18n error messages
    if not req_info.demetrius_perms.Check(permissions.EDIT_PROJECT):
      raise permissions.PermissionException(
        'You are not allowed to administer this project')

  def GatherPageData(self, request, req_info):
    """Build up a dictionary of data values to use when rendering the page."""

    # Help prevent owners from deleting their role.  But, there is no need to
    # warn site admins because they won't lose access to the project that way.
    check_abandonment = (
      req_info.logged_in_user_id in req_info.project.owner_ids_list() and
      req_info.user_pb and not req_info.user_pb.is_site_admin())

    page_data = {
      'admin_tab_mode': constants.ADMIN_TAB_MEMBERS,
      'check_abandonment': ezt.boolean(check_abandonment),
      'errors': req_info.errors or ezt_google.EZTError(),
      }

    members = helpers.BuildProjectMembers(req_info.project, self.demetrius_persist)
    page_data.update(members)

    post.URLCommandAttacksEncode(page_data, req_info.logged_in_user_id)
    return page_data

  def ProcessForm(self, request, req_info):
    """Process the posted form."""
    errors = ezt_google.EZTError()
    post_data = post.ProcessPOSTBody(
        request, framework.constants.MAX_POST_BODY_SIZE)
    if post_data is None:
      # An error occurred and the response was generated. We're done.
      raise framework.helpers.AlreadySentResponse()

    post.URLCommandAttacksCheck(post_data, req_info.logged_in_user_id)

    self.demetrius_persist.LockProject(req_info.project_name)
    try:
      owner_ids, member_ids = self._ParseMembers(post_data, errors)

      total_num_people = len(owner_ids) + len(member_ids)
      if total_num_people > constants.MAX_PROJECT_PEOPLE:
        errors.people = ('Too many users entered.  The combined limit is %d.' %
                         constants.MAX_PROJECT_PEOPLE)

      if not errors.AnyErrors():
        self.demetrius_persist.UpdateLockedProject(
          req_info.project_name, self.conn_pool,
          owner_ids=owner_ids, member_ids=member_ids)

    finally:
      self.demetrius_persist.UnlockProject(req_info.project_name)

    if errors.AnyErrors():
      req_info.PrepareForSubrequest(req_info.project_name, errors)
      self.Handler(request, req_info=req_info)
    else:
      url = framework.helpers.FormatAbsoluteURL(
        req_info, constants.ADMIN_MEMBERS_PAGE_URL, request,
        saved=1, ts=int(time.time()))
      http.SendRedirect(url, request)

  def _ParseMembers(self, post_data, errors):
    """Process the project members section of the admin page."""
    owner_ids = self._ParseUsernames('owners', post_data, [], errors)
    member_ids = self._ParseUsernames('members', post_data, owner_ids, errors)
    return owner_ids, member_ids


  def _ParseUsernames(self, usernames_field, post_data, ignore_ids, errors):
    """Parse all usernames from a text field and return a list of user ids.

    Args:
      usernames_field: HTML text area form field name.
      post_data: HTTP POST data including a value for usernames_field.
      ignore_ids: a list of user ids to ignore, because they are already
        listed in a more powerful role in this project.
      errors: EZTError object to record parsing errors.

    Result:
      A) A list of user ids or full email addresses for the users named.  Or,
      B) An empty list, if the usernames_field was not in post_data.
         (Browsers might not send the field if it was '')
    """

    if usernames_field not in post_data:
      return []

    usernames_text = post.LoadFieldFromPOST(usernames_field, post_data)
    usernames_list = _RE_EMAIL_SEPARATORS.split(usernames_text)

    user_ids = []
    for edit_name in usernames_list:
      if not edit_name:
        continue  # skip separators
      try:
        user_id = self.demetrius_persist.LookupUserIdByEmail(
          framework.helpers.ConvertEditNameToEmail(edit_name))
        if user_id not in user_ids and user_id not in ignore_ids:
          user_ids.append(user_id)
      except framework.helpers.NoSuchUserException, e:
        errors.__setattr__(usernames_field, 'No such user: %s' % edit_name)
    return user_ids


class ProjectAdminAdvanced(pageclasses.DemetriusPage):
  """A page with project state options for the Project Owner(s)."""

  _PAGE_TEMPLATE = 'demetrius/project-admin-advanced-page.ezt'
  _MAIN_TAB_MODE = constants.MAIN_TAB_ADMIN

  def AssertBasePermission(self, req_info):
    """Make sure that the logged in user has permission to view this page.

    Args:
      req_info: commonly used info parsed from the request.
    """

    pageclasses.DemetriusPage.AssertBasePermission(self, req_info)
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

    state = req_info.project.state()
    perms = req_info.demetrius_perms
    offer_delete = state not in [demetrius_pb.Project.DOOMED,
                                 demetrius_pb.Project.DELETE_PENDING]
    offer_hide = (perms.Check(permissions.PUBLISH_PROJECT) and
                  state in [demetrius_pb.Project.LIVE,
                            demetrius_pb.Project.MOVED])
    # The only way out of DOOMED is for an admin to re-publish.
    offer_publish = (perms.Check(permissions.PUBLISH_PROJECT) and
                     state in [demetrius_pb.Project.HIDDEN,
                               demetrius_pb.Project.DOOMED])
    offer_undelete = state in [demetrius_pb.Project.DELETE_PENDING]
    offer_doom = (perms.Check(permissions.PUBLISH_PROJECT) and
                  state not in [demetrius_pb.Project.DOOMED])
    page_data = {
      'admin_tab_mode': constants.ADMIN_TAB_ADVANCED,

      'offer_delete': ezt.boolean(offer_delete),
      'offer_hide': ezt.boolean(offer_hide),
      'offer_publish': ezt.boolean(offer_publish),
      'offer_undelete': ezt.boolean(offer_undelete),
      'offer_doom': ezt.boolean(offer_doom),
      'default_doom_reason': constants.DEFAULT_DOOM_REASON,
      }

    post.URLCommandAttacksEncode(page_data, req_info.logged_in_user_id)
    return page_data

  def ProcessForm(self, request, req_info):
    """Process the posted form.

    Args:
      request: the HTTP request being processed.
      req_info: commonly used info parsed from the request.
    """

    post_data = post.ProcessPOSTBody(
        request, framework.constants.MAX_POST_BODY_SIZE)
    if post_data is None:
      # An error occurred and the response was generated. We're done.
      raise framework.helpers.AlreadySentResponse()

    post.URLCommandAttacksCheck(post_data, req_info.logged_in_user_id)

    state = req_info.project.state()
    perms = req_info.demetrius_perms

    if ('deletebtn' in post_data and state != demetrius_pb.Project.DOOMED):
      self.demetrius_persist.DeleteProject(req_info.project_name)

    elif 'doombtn' in post_data: # Go from any state to DOOMED
      reason = None
      if 'reason' in post_data: reason = post_data['reason'][0]
      self.demetrius_persist.DoomProject(req_info.project_name, reason)

    elif 'hidebtn' in post_data: # Go from any state to HIDDEN
      if not perms.Check(permissions.PUBLISH_PROJECT):
        raise permissions.PermissionException(
          'You are not allowed to hide projects')
      self.demetrius_persist.HideProject(req_info.project_name,
                                         self.conn_pool)

    elif 'publishbtn' in post_data: # Go from any state to LIVE
      if not perms.Check(permissions.PUBLISH_PROJECT):
        raise permissions.PermissionException(
          'You are not allowed to publish projects')
      self.demetrius_persist.PublishProject(req_info.project_name,
                                            self.conn_pool)

    elif 'undeletebtn' in post_data: # Go from only DELETE_PENDING to LIVE.
      if state != demetrius_pb.Project.DELETE_PENDING:
        raise permissions.PermissionException(
          'This project is not pending deletion, you cannot republish it.')
      self.demetrius_persist.PublishProject(req_info.project_name,
                                            self.conn_pool)

    url = framework.helpers.FormatAbsoluteURL(
      req_info, constants.ADMIN_ADVANCED_PAGE_URL, request,
      saved=1, ts=int(time.time()))
    http.SendRedirect(url, request)


def _ExtractPairs(post_data, key_prefix, other_key_prefix, errors,
    section_name):
  """Find and return matching pairs of values in the given dict.

  The pairs consist of a label and an value (URL or Google Group ID).
  The values are only extracted if the user supplies both the label and the
  corresponding url.  Values are sorted by key so that the same order is kept
  before and after editing.
  """

  relevant_keys = [key for key in post_data.iterkeys()
    if key.startswith(key_prefix)]

  relevant_keys.sort()
  skip = len(key_prefix)
  result = []

  for key in relevant_keys:
    other_key = '%s%s' % (other_key_prefix, key[skip:])

    label = post_data[key][0].strip()
    value = post_data[other_key][0].strip()

    if value == 'http://':
      value = ''  # Remove text that was just a prompt.

    # any pair with a non-default value gets added to the result, as this
    # is necessary for error handling
    if label or value:
      result.append((label, value))

      if label and value:
        #logging.debug("Found valid pair for: %s/%s" % (key, other_key))
        pass
        
      # pairs with a missing value cause an error attribute to be set
      else:
        setattr(errors, section_name, True)
        #logging.debug("Input contained a partial pair for: %s/%s"
          #% (key, other_key))

  return result
