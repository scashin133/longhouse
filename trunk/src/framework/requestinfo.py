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

"""Class to hold information parsed from a request.

To simplify our servlets and avoid duplication of code, we parse some
info out of the request as soon as we get it and then pass a req_info
object to the servlet-specific request handler methods.
"""

import sys
import time
import urllib

from twisted.python import log

from framework import constants
from framework import helpers
from twisted.python import log

from demetrius import permissions

from common import http
from bo import demetrius_pb

class ParsedURL(object):
    
    def __init__(self, request):
        self.path_ = request.path
        self.args = request.args
    
    def path(self):
        return self.path_
    
    def GetQueryComponent(self, name):
        return self.args[name]

class RequestInfo(object):
  """A class to hold information parsed from the HTTP request.

  This RequestInfo class is used for Demetrius pages, and it should
  also serve as a base class for component-specific subclasses that
  parse additional request parameters needed in other components.
  """

  # Gmail users have email addresses from these domains.
  _GMAIL_DOMAINS = ['gmail.com', 'googlemail.com']

  def __init__(self):
    """Initialize the RequestInfo object."""
    self.synthetic_params = {}
    self.errors = None



  def ParseURI(self, request):
    """Parse generic information from the URI itself."""
    self.hostport = request.getHeader('host')
    self.current_page_url = 'http://%s%s' % (self.hostport, request.path)

    self.url = ParsedURL(request)

    self.current_page_url_encoded = urllib.quote_plus(self.current_page_url)
    log.msg('Request: %s' % self.current_page_url)

  def ExtractCommonParameters(self, request, conn_pool, demetrius_persist):
    """Parse out request parameters that are used on several pages."""
    path_info = self.url.path()

    self.project_name = None
    self.project = None
    if path_info.startswith('/p/'):
      self.project_name = path_info.split('/')[2]
      self.project_promise = helpers.Promise(
        demetrius_persist.GetProject, self.project_name)

    viewed_username = None
    self.viewed_user_id = None
    self.viewed_user_pb = None
    if path_info.startswith('/u/'):
      viewed_username = path_info.split('/')[2].strip()

      #try:
        #self.viewed_user_id = demetrius_persist.LookupUserIdByUsername(
          #viewed_username)
      #except helpers.NoSuchUserException:
      #  log.msg('username %s not found' % viewed_username)

      # If we have an id, try and get the user pb.
      # If that user exists but does not have a Demetrius account,
      # this call will return None, so a 404 will still be raised.
      #if self.viewed_user_id is not None:
        #self.viewed_user_pb = demetrius_persist.GetUser(self.viewed_user_id)
      #if self.viewed_user_id is None:
        #raise helpers.NoSuchPageException()
      #self.viewed_user = helpers.UserIDProxy(self.viewed_user_id, self.demetrius_persist)
    
    #The above commented-out block breaks when the NoSuchPageException is thrown.
    #instead of showing a helpful error message, the page simply doesn't render
    #before you have a chance to perform logic in the page's controlling code.
    #instead, in demetrius/user_profile.py, check to see if viewed_user_id is not null
    #and get the user_pb there. With this technique, there is no need to make a
    #viewed_user proxy.
    try:
        self.viewed_user_id = demetrius_persist.LookupUserIdByEmail(viewed_username)
    except helpers.NoSuchUserException:
        pass
    self.start = self.GetIntParam('start', default_value=0)
    self.num = self.GetIntParam('num', default_value=100)

    link_generation_timestamp = self.GetIntParam('ts', default_value=0)
    now = int(time.time())
    if now - link_generation_timestamp < constants.LINK_EXPIRATION_SEC:
      self.ts_links = 'valid'
    else:
      self.ts_links = 'expired'

    self.continue_url = request.getHeader('referer')

    # Search scope, a.k.a., canned query ID
    self.can = self.GetIntParam('can', default_value=2)

    # Search query
    self.query = self.GetParam('q', default_value='')

    # Sorting of search results (needed for result list and flipper)
    self.sort_spec = self.GetParam('sort', default_value='',
                                   antitamper_re=constants.SORTSPEC_RE)

    # Used to show message confirming item was updated
    self.updated = self.GetIntParam('updated')

    # Used to show message confirming item was accepted
    self.thanks = self.GetIntParam('thanks')

    # Used to show message confirming items imported
    self.imported = self.GetIntParam('imported')

    # Used to show message confirming items deleted
    self.deleted = self.GetIntParam('deleted')

    # If present, we will show message confirming that data was saved
    self.saved = self.GetParam('saved')

  def ParseUserInfo(self, request, conn_pool, demetrius_persist,
                    tool_permission_dict):
    """Get information about the current user (if any) from the request.

    Args:
      request: the HTTP request.
      conn_pool: ConnectionPool object that interfaces to AuthSub.
      demetrius_persist: DemetriusPersist interface to storage backends.
      tool_permission_dict: Dictionary used to build a PermissionSet
        appropriate for the current user in the current tool (e.g.,
        DIT).
    """
    
    session = request.getSession()
    
    try:
        self.logged_in_user_id = int(session.logged_in_user_id)
    except AttributeError:
        self.logged_in_user_id = None
        
    
    self.logged_in_user = None
    self.logged_in_user_has_gmail = False
    self.logged_in_user_verified = False
    self.user_pb = None
    cui = None
    
    if not self.logged_in_user_id is None:
        self.user_pb = demetrius_persist.GetUser(self.logged_in_user_id)
        self.logged_in_user = helpers.UserIDProxy(self.logged_in_user_id, 
                    demetrius_persist,
                    self.user_pb)
        # TODO Actually check for this.  For now assume all users have been verified.
        if self.user_pb.is_validated() == 1:
          self.logged_in_user_verified = True
        else:
          self.logged_in_user_verified = False  
        email_domain = self.logged_in_user.email.split('@')[-1]
        if email_domain in self._GMAIL_DOMAINS:
          self.logged_in_user_has_gmail = True

    # TODO: remove this line
    serialized_user_pb, user_info = None, None

    if conn_pool:
      # TODO(students): get info about logged in user.
      serialized_user_pb, user_info = None, None
      if serialized_user_pb:
        self.user_pb = demetrius_pb.User(serialized_user_pb)

    if user_info:
      self.logged_in_user_id = user_info.userid()
      self.logged_in_user_verified = user_info.verified()
      self.logged_in_user = helpers.UserIDProxy(
        self.logged_in_user_id, conn_pool, client_user_info=user_info)
      email_domain = self.logged_in_user.email.split('@')[-1]
      if email_domain in self._GMAIL_DOMAINS:
        self.logged_in_user_has_gmail = True

    self._WaitForProject()

    self.demetrius_perms = permissions.GetPermissions(
      request, self.user_pb, self.logged_in_user_id,
      self.logged_in_user_verified,
      self.logged_in_user_has_gmail, self.project)

    self.tool_perms = None
    if tool_permission_dict:
      self.tool_perms = permissions.GetPermissions(
        request, self.user_pb, self.logged_in_user_id,
        self.logged_in_user_verified,
        self.logged_in_user_has_gmail, self.project,
        permissions_dict=tool_permission_dict)

  def _WaitForProject(self):
    """If we requested a project, block until we get it."""
    if not self.project_name: return
    self.project = self.project_promise.WaitAndGetValue()
    if not self.project:
      raise helpers.NoSuchPageException()

  def PrepareForSubrequest(self, project_name, errors, **kw):
    """Expose the resuls of form processing as if it was a new GET.

    This method is called only when the user submits a form with invalid
    information which they are being asked to correct.  Updating the req_info
    object allows the normal page Handler method to popluate the form with
    the entered values and error messages.
    """

    self.project_name = project_name
    self.errors = errors
    self.synthetic_params = kw

  def GetParam(self, query_param_name, default_value=None,
               antitamper_re=None):
    """Get a string query parameter from the synthetic params or URL."""
    if query_param_name in self.synthetic_params:
      result = self.synthetic_params[query_param_name]
    else:
        try:
            result = self.url.GetQueryComponent(query_param_name)[0]
        except KeyError:
            return default_value
        
    if result is not None:
      if antitamper_re is not None:
        if not antitamper_re.match(result):
          log.msg('User seems to have tampered with %s field: %s'
                       % (query_param_name, result))
          raise helpers.TamperingException(query_param_name, result)
      return result
    return default_value

  def GetIntParam(self, query_param_name, default_value=None):
    """Get an integer param from the synthetic params or URL, or default."""
    if query_param_name in self.synthetic_params:
      return self.synthetic_params[query_param_name]
    try:
      return int(self.url.GetQueryComponent(query_param_name)[0])
    except (TypeError, ValueError, KeyError):
      return default_value

  def GetIntListParam(self, query_param_name, default_value=None):
    """Get a list of ints from the synthetic params or URL, or default."""
    if query_param_name in self.synthetic_params:
      return self.synthetic_params[query_param_name]
    param = self.url.GetQueryComponent(query_param_name)
    if not param:
      return default_value
    try:
      return [int(p) for p in param]
    except (TypeError, ValueError):
      return default_value

  def GetLongParam(self, query_param_name, default_value=None):
    """Get an long int param from the synthetic params or URL, or default."""
    if query_param_name in self.synthetic_params:
      return self.synthetic_params[query_param_name]
    try:
      return long(self.url.GetQueryComponent(query_param_name))
    except (TypeError, ValueError, KeyError):
      return default_value


if __name__ == '__main__':
  sys.exit('This is not meant to be run as a standalone program. Exiting.')
