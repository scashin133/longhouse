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

"""Base classes for web pages for the Demitrius component and other components.

The DemetriusPage base class provides a Handler that conviently drives
the process of parsing the request, checking base permissions,
gathering common page information, gathering page-specific
information, and adding on-page debugging information (when
appropriate).  Subclasses can simply implement the page-specific logic.

Summary of page classes:
  DemetriusPage: abstract base class for all demetrius pages.
  ContextDebugItem: displays ezt_data elements for on-page debugging.
"""

import sys
import time
import urllib

from twisted.python import log

from ezt import ezt

from common import http
from common import post
from common import ezt_google
#from common import validate

from bo import demetrius_pb
from framework import constants
from framework import requestinfo
from framework import persist
from framework import helpers
from framework import user

from demetrius import permissions
import demetrius.constants


class DemetriusPage(object):
  """Base class for all Demetrius web pages.

  Defines a framework of methods that build up parts of the EZT
  context.
  """

  _TEMPLATE_PATH = 'templates/'

  _PAGE_TEMPLATE = None  # Normally overriden in subclasses.
  _MAIN_TAB_MODE = None  # Normally overriden in subclasses.
  _REQ_INFO_FACTORY = requestinfo.RequestInfo
  _TOOL_PERMISSION_DICT = {}

  def __init__(self, conn_pool, demetrius_persist,
               universal_ezt_data, worktable=None):
    """Load and parse the template, saving it for later use."""
    if self._PAGE_TEMPLATE: # specified in subclasses
      template_path = self._TEMPLATE_PATH + self._PAGE_TEMPLATE
      self.template = ezt_google.GoogleTemplate(template_path)
    self.demetrius_persist = demetrius_persist
    self.universal_ezt_data = universal_ezt_data
    self.worktable = worktable
    #self.users = user.Users(conn_pool)
    self.conn_pool = conn_pool

  def Handler(self, request, req_info=None):
    """Collect page-specific and generic info, then render the page.

    Normally, this method is called directly from the server with just
    a request and no req_info.  In this case, it makes a req_info to
    hold information parsed from the request.

    This method can also be called with a pre-made req_info.  This is
    useful when a form handler has detected a problem with the user's
    input and needs to re-render the page with errors highlighted.
    """

    try:
      if req_info is None:
        req_info = self._REQ_INFO_FACTORY()

      req_info.ParseURI(request)
      req_info.ExtractCommonParameters(
        request, self.conn_pool, self.demetrius_persist)
      req_info.early_promise = self.EarlyPageProcessing(request, req_info)

      req_info.ParseUserInfo(
        request, self.conn_pool, self.demetrius_persist,
        self._TOOL_PERMISSION_DICT)

      self.AssertBasePermission(req_info)
      ezt_data = self.universal_ezt_data.copy()
      ezt_data.update(self.GatherBaseData(request, req_info))
      ezt_data.update(self.GatherPageData(request, req_info))
      ezt_data.update(self.GatherDebugData(request, req_info, ezt_data))

      self.GetTemplate(ezt_data).WriteResponse(request, ezt_data)

    except permissions.PermissionException, e:
      log.msg('got PermissionException %s' % e)
      if req_info.logged_in_user_id is None:
        # If not logged in, let them log in
        url = ('/login?followup=%s' %
               req_info.current_page_url_encoded)
        http.SendRedirect(url, request, code=http.HTTP_FOUND)
      else:
        # If the user simply does not have permission: 403 permission denied
        log.msg('permission error: %s' % e)
        http.HttpResponse(request, code=http.HTTP_PERMISSION_DENIED)

    except helpers.RedirectException, e:
      http.SendRedirect(e.url, request)

    except helpers.NoSuchPageException, e:
      http.HttpResponse(request, code=http.HTTP_NOT_FOUND)

    except helpers.AlreadySentResponse:
      pass  # If servlet already sent response, then do nothing more.

    except post.TokenIncorrect:
      log.msg('bad url command attack token')
      http.BadRequest(request)

    except helpers.TamperingException:
      # a message should have already been logged.
      http.BadRequest(request)

    # Allow any other exception to propogate up so we get a error page with a stack trace
    # TODO: change this back graceful exception handling
    #except:  # Log any other exception and show a generic error msg
        #log.err('Failure rendering: %s' % self._PAGE_TEMPLATE)
        #http.HttpResponse(request, code=http.HTTP_INTERNAL_SERVER_ERROR)

  def FormHandler(self, request):
    """Parse the request, check base perms, and call form-specific code."""
    try:
      req_info = self._REQ_INFO_FACTORY()
      req_info.ParseURI(request)
      req_info.ExtractCommonParameters(
        request, self.conn_pool, self.demetrius_persist)
      req_info.early_promise = self.EarlyFormProcessing(request, req_info)
      req_info.ParseUserInfo(
        request, self.conn_pool, self.demetrius_persist,
        self._TOOL_PERMISSION_DICT)

      self.AssertBasePermission(req_info)
      form_result = self.ProcessForm(request, req_info)

    except permissions.PermissionException, e:
      log.msg('got PermissionException %s' % e)
      http.BadRequest(request)

    except post.TokenIncorrect:
      log.msg('bad url command attack token')
      http.BadRequest(request)

    except helpers.AlreadySentResponse:
      pass

    except persist.MidAirCollision, e:
      log.msg('mid-air collision detected.')
      collision_page_url = constants.ARTIFACT_COLLISION_PAGE_URL
      if not req_info.project_name:
        # An editing collision can happen outside a demetrius project
        # as part of Project Galleries editing.
        collision_page_url = constants.NONPROJECT_COLLISION_PAGE_URL
      url = helpers.FormatAbsoluteURL(
        None, collision_page_url, request,
        project_name=req_info.project_name,
        name=e.name, continue_url=urllib.quote_plus(e.continue_url),
        ts=int(time.time()))
      http.SendRedirect(url, request)

    except helpers.TamperingException:
      # a message should have already been logged.
      http.BadRequest(request)

    except:  # Log any other exception and show a generic error msg
      log.err('Failure rendering: %s' % self._PAGE_TEMPLATE)
      http.HttpResponse(request, code=http.HTTP_INTERNAL_SERVER_ERROR)

    finally: # If the form resulted in a deferred, return it. The twisted resources know what to do with it
        # TODO: use isinstance() here instead?
        if str(form_result.__class__) == 'twisted.internet.defer.Deferred':
            return form_result


  def GetTemplate(self, ezt_data):
    """Get the template to use for writing the http response.

    Defaults to self.template.  This method can be overwritten in subclasses
    to allow dynamic template selection based on ezt_data.

    Args:
      ezt_data: A dict of data for ezt rendering, containing base ezt data,
        captcha data, page data, and debug data.

    Returns:
      The template to be used for writing the http response.
    """
    return self.template

  def GetAvailableSections(self):
    """Return a comma-separated list of available page sections or None."""
    return None

  def AssertBasePermission(self, req_info):
    """Make sure that the logged in user has permission to view this page.

    Subclasses should call super, then check additional permissions
    and raise a PermissionException if the user is not authorized to
    do something.
    """

    if (req_info.project_name and
        not req_info.demetrius_perms.Check(permissions.VIEW_PROJECT)):
      raise permissions.PermissionException(
          'You are not allowed to view this project')

  def GatherBaseData(self, request, req_info):
    """Return a dict of info used on almost all pages."""
    project_alert = None
    if req_info.project:
      state = req_info.project.state()
      if state == demetrius_pb.Project.HIDDEN:
        project_alert = 'This project is only visible to owners and members.'
      elif state == demetrius_pb.Project.DELETE_PENDING:
        project_alert = ('This project is only visible to owners and members. '
                         'It is scheduled for deletion.')
      elif state == demetrius_pb.Project.DOOMED:
        project_alert = ('This project is only visible to owners and members. '
                         'It is scheduled for deletion: %s.' %
                         req_info.project.delete_reason())

    project_summary = ''
    if req_info.project:
      project_summary = req_info.project.summary()

    project_repository = ''
    if req_info.project:
      project_repository = req_info.project.repository_url()

    project_pb_or_none = None
    if req_info.project:
      project_pb_or_none = ezt_google.PBProxy(req_info.project)

    shown_sections = None  # Most templates don't even have sections.
    sections = self.GetAvailableSections()
    if sections:
      shown_sections = helpers.SectionSet(
          req_info.GetParam('show', sections))

    return {
      'page_template': self._PAGE_TEMPLATE,
      'main_tab_mode': self._MAIN_TAB_MODE,
      'project_summary': project_summary,
      'project_repository': project_repository,
      'projectname': req_info.project_name,
      'project': project_pb_or_none,
      'logged_in_user': req_info.logged_in_user,
      'logged_in_user_has_gmail':
        ezt.boolean(req_info.logged_in_user_has_gmail),
      'logged_in_user_verified': ezt.boolean(req_info.logged_in_user_verified),
      'demetrius_perms': req_info.demetrius_perms,
      'tool_perms': req_info.tool_perms,
      'currentPageURL': req_info.current_page_url,
      'currentPageURLEncoded': req_info.current_page_url_encoded,
      'continue_url': req_info.continue_url,
      'shown_sections': shown_sections,

      # for project search (some also used in issue search)
      'start': req_info.start,
      'num': req_info.num,
      'q': None,

      # for alert.ezt
      'ts_links': req_info.ts_links,
      'saved': req_info.saved,
      'updated': req_info.updated,
      'deleted': req_info.deleted,
      'thanks': req_info.thanks,
      'imported': req_info.imported,
      'project_alert': project_alert,
      }

  def EarlyPageProcessing(self, request, req_info):
    """Return a Promise to do *unathenticated* work in parallel, or None."""
    return None

  def GatherPageData(self, request, req_info):
    """Return a dict of page-specific values."""
    return {}

  def EarlyFormProcessing(self, request, req_info):
    """Return a Promise to do *unathenticated* work in parallel, or None."""
    return None

  def GatherDebugData(self, request, req_info, ezt_data):
    """Return debugging info for display at the very bottom of the page."""
    path_info = req_info.url.path().split('/')
    if 'dbg' in path_info:
      return {
        'dbg': 'on',
        'debug': [ContextDebugItem(key, val) for key, val in ezt_data.items()],
        }
    else:
      debug_uri = ''
      if req_info.project_name is None:
        debug_uri = '/dbg' + request.path
      elif 'p' in path_info:
        project_position = path_info.index('p') + 1
        trailing_path = path_info[project_position + 1:]
        debug_uri = 'http://%s/p/%s/dbg/%s?%s' % (
          req_info.hostport, req_info.project_name, '/'.join(trailing_path),
          req_info.query)
      return {
        'debug_uri': debug_uri,
        'dbg': 'off',
        'debug': [('none', 'recorded')],
        }

  def MakePromise(self, callback, *args):
    """Make a Promise object to compute the callback using a python thread."""
    return helpers.Promise(callback, *args)


class ContextDebugItem(object):
  """Wrapper class to generate on-screen debugging output."""

  def __init__(self, key, val):
    """Store the key and generate a string for the value."""
    self.key = key
    if isinstance(val, list):
      nested_debug_strs = [self.StringRep(v) for v in val]
      self.val = '[%s]' % ', '.join(nested_debug_strs)
    else:
      self.val = self.StringRep(val)

  def StringRep(self, val):
    """Make a useful string representation of the given value."""
    try:
      return val.DebugString()
    except AttributeError:
      try:
        return str(val.__dict__)
      except AttributeError:
        return repr(val)

if __name__ == '__main__':
  sys.exit('This is not meant to be run as a standalone program. Exiting.')
