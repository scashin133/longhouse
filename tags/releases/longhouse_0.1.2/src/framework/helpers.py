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

"""Helper functions and classes used by the Demetrius pages.

Each function garthers data for one section of a Demetrius page.  The functions
place the data in a context, which is passed to EZT to output the HTML.
"""

import sys
import urllib
import threading
import time

from ezt import ezt

from twisted.python import log

from common import post
from common import http
from common import ezt_google
from common import timestr
#from common import pageclasses
#from bo import demetrius_pb
from framework import constants



class Promise(object):
   """Class for promises to deliver a value in the future.

   A thread is started to run callback(args), that thread
   should return the value that it generates, or raise an expception.
   p.WaitAndGetValue() will block until a value is available.
   If an exception was raised, p.WaitAndGetValue() will re-raise the
   same exception.
   """

   def __init__(self, callback, *args):
     """Initialize the promise and immediately call the supplied function.

     Args:
       callback: Function that takes the args and returns the promise value.
       *args:  Any arguments to the target function.
     """
     self.has_value = False
     self.value = None
     self.semaphore = threading.Semaphore(0)
     self.callback = callback
     self.exception = None
     t = threading.Thread(target=self._WorkOnPromise, args=args)
     t.start()

   def _WorkOnPromise(self, *args):
     """Run callback to compute the promised value.  Save any exceptions."""
     try:
       self.value = self.callback(*args)
     except Exception,e:
       log.msg(e)
       self.exception = e
     self.has_value = True
     self.semaphore.release()

   def WaitAndGetValue(self):
     """Block until my value is available, then return it or raise exception."""
     if not self.has_value:
       self.semaphore.acquire()
     if self.exception:
       raise self.exception
     return self.value


class UserIDProxy(object):
  """Wrapper class that makes it easier to display a User via EZT.

  Sets the variables: email, username, and fullname.
  """

  def __init__(self, user_id, demetrius_persist, user_pb=None, client_user_info=None):
    """Store relevant values for later display by EZT."""
    self.email = None
    self.profile_url = None
    self.display_name = None
    self.edit_name = ''
    self.username = ''
    self.fullname = ''  # For now, always left as ''.
    self.user_id = user_id
    self.projects_owned = []
    self.projects_member = []
    self.demetrius_persist = demetrius_persist
    
    if user_id == constants.NO_USER_SPECIFIED:
        self.email = ''
        self.profile_url = ''
        self.display_name = ''
    elif user_id or user_id == 0:
        
        if user_pb is None:
            user_pb = demetrius_persist.GetUser(user_id)
        
        self.email = user_pb.account_email()
        (self.username, self.user_domain, self.is_gmail_address,
            self.obscured) = ParseAndObscureAddress(self.email)
        self.display_name = '%s...@%s' % (self.obscured, self.user_domain)
        self.edit_name = self.email
        self.profile_url = '/u/%s/' % self.email
        self.projects_owned = user_pb.owner_of_projects_list()
        self.projects_member = user_pb.member_of_projects_list()
        if self.is_gmail_address:
            self.display_name = self.email
            self.edit_name = self.email
            self.profile_url = '/u/%s/' % self.email
            self.username = self.email
        else:
            self.display_name = self.email
            self.edit_name= self.email
            self.profile_url = '/u/%s/' % self.email
            self.username = self.email

def MakeAllUserIDProxies(conn_pool, demetrius_persist, *args):
  """Make UserIDProxy's for many users in one batch.

  Args:
    conn_pool: ConnectionPool object that interfaces to AuthSub.
    *args: any number of lists of user ids. E.g., project owners and members.

  Returns: { distinct_user_id : UserIDProxy(distinct_user_id), ... }
    Returns a dictionary of distinct user ids from all the given lists with
    the correpsonding UserIDProxy for each user..
  """
  unique_user_ids = []
  for user_id_list in args:
    for user_id in user_id_list:
      if user_id not in unique_user_ids:
         unique_user_ids.append(user_id)

  #cuis_by_id = conn_pool.GetClientUserInfoBatch(unique_user_ids)
  proxies_by_id = dict([(user_id,
                         UserIDProxy(
                           user_id, demetrius_persist,
                           #client_user_info=cuis_by_id[user_id]
                           ))
                        for user_id in unique_user_ids])
  return proxies_by_id


def ParseAndObscureAddress(email):
  """Break the given email into username and domain, and obscure if needed.

  Args:
    email: string email address to process

  Returns (username, domain, is_gmail_address, obscured_username).
  The obscured_username is trucated the same way that Google Groups does it.
  """
  if '@' in email:
    username, user_domain = email.split('@')
  else:  # don't fail if AuthSub has some bad data
    username, user_domain = email, ''

  is_gmail_address = user_domain in ['gmail.com', 'googlemail.com']
  obscured_username = username[0 : min(8, max(1, len(username) - 3))]

  return (username, user_domain, ezt.boolean(is_gmail_address),
          obscured_username)


def ConvertEditNameToEmail(edit_name):
  """Convert an edit_name to full email addr by adding gmail.com, if needed."""
  if '@' in edit_name:
    return edit_name  # edit_name was already a full email address.
  else:
    return edit_name + '@gmail.com'  # edit_name was in short-hand for gmail.


def FormatAbsoluteURL(cur_req_info, servlet_name, request, project_name=None,
                      **kw):
  """Return an absolute URL to a servlet with old and new params.

  Args:
    cur_req_info: parsed info the current request.
    servlet_name: site or project-local url fragement of dest page.
    request: the current HTTP request object.
    project_name: the destination project name, normally only specified
      in cases where the destination project did not exist prior to this
      operation.
    kw: additional query string paramaters may be specified as named
      arguments to this funcion.
  """

  relative_url = FormatURL(cur_req_info, servlet_name, **kw)
  host = request.received_headers['host']
  if not project_name and cur_req_info:
    project_name = cur_req_info.project_name
  if project_name:
    return 'http://%s/p/%s%s' % (host, project_name, relative_url)
  else:
    return 'http://%s%s' % (host, relative_url)


def FormatURL(cur_req_info, servlet_name, **kw):
  """Return a relative URL to a servlet with old and new params."""

  # Try to preserve all the query string params that we normally keep.
  if cur_req_info:
    new_params = {
      'can': cur_req_info.GetParam('can'),
      'start': cur_req_info.GetParam('start'),
      'num': cur_req_info.GetParam('num'),
      'q': cur_req_info.GetParam('q'),
      'colspec': cur_req_info.GetParam('colspec'),
      'sort': cur_req_info.GetParam('sort'),
      }
  else:
    new_params = {}

  # Then, add any that were passed in as additional arguments
  new_params.update(kw)

  param_strings = ['%s=%s' % (k, v) for k, v in new_params.items()
                   if v is not None]
  if param_strings:
    return '%s?%s' % (servlet_name, '&'.join(param_strings))
  else:
    return servlet_name


class SectionSet(object):
  """An easy way to specify which sections of a page to display in EZT."""

  def __init__(self, section_list_spec):
    """Remember a comma-separated list of sections names."""
    self.section_names = section_list_spec.split(',')

  def __getattr__(self, attrname):
    """Return a EZT boolean if attrname matches a section name."""
    return ezt.boolean(attrname in self.section_names)


class AbstractPageSetup(object):
  """Abstract base class for all component-specific PageSetup classes.

  This class provides reusable methods to instantiate and register servlets.
  """

  def _SetupProjectPage(self, handler, url):
    """Register a handler for a project page, assuming our conventions."""
    self.server.RegisterPerProjectHandler(url, handler)
    
    # TODO find out what RedirectInScope actually does
    # if url.endswith('/'):  # allow user to type name without trailing slash
    #       redirect = pageclasses.RedirectInScope(url, 'p')
    #       self.server.RegisterPerProjectHandler(url[:-1], redirect.SendRedirect)

    # Another way to access the same handler w/ debugging turned on,
    # only available from Google internal IP addresses.
    self.server.RegisterPerProjectHandler('/dbg' + url, handler, private=True)

  def _SetupProjectForm(self, formhandler, url, does_write=None):
    """Register a project form handler, assuming our conventions."""
    self.server.RegisterPerProjectHandler(
        url, formhandler, does_write=does_write)

  def _SetupUserPage(self, handler, url):
    """Register a handler for a user page, assuming our conventions."""
    self.server.RegisterPerUserHandler(url, handler)

    # TODO find out what RedirectInScope actually does
    if url.endswith('/'):  # allow user to type name without trailing slash
       #redirect = pageclasses.RedirectInScope(url, 'u')
       self.server.RegisterPerUserHandler(url[:-1], handler)

  def _SetupUserForm(self, formhandler, url):
    """Register a form handler for a user page, assuming our conventions."""
    self.server.RegisterPerUserHandler(url, formhandler)

  def _SetupSitePage(self, handler, url):
    """Register a handler for a page, assuming our conventions ."""
    self.server.RegisterHandler(url, handler)

    # Another way to access the same handler w/ debugging turned on,
    # only available from local IP addresses.
    self.server.RegisterHandler('/dbg' + url, handler, private=True)

  def _SetupSiteForm(self, formhandler, url):
    """Register a form handler, assuming our conventions."""
    self.server.RegisterHandler(url, formhandler)

  def _SetupStaticPage(self, rsrc_name, url):
    """Register a static page, e.g., a CSS file."""
    year_from_now = int(time.time()) + constants.SECS_PER_YEAR
    cache_headers = [
      ('Cache-Control',
       'max-age=%d, public' % constants.SECS_PER_YEAR),
      ('Last-Modified', timestr.TimeForHTMLHeader()),
      ('Expires', timestr.TimeForHTMLHeader(when=year_from_now)),
      ]
    page = pageclasses.StaticPage(rsrc_name, response_headers=cache_headers)
    self.server.RegisterHandler(url, page.DumpHTML)

  def _SetupDeferredPage(self, handler, url):
      self.server.RegisterDeferred(url, handler)

  def _SetupPerProjectDeferredPage(self, handler, url):
      self.server.RegisterPerProjectDeferred(url, handler)


class Error(Exception):
  """Base class for errors from this module."""


class RedirectException(Error):
  """The servlet wants to redirect rather than render a page template."""

  def __init__(self, message, url):
    Error.__init__(self, message)
    self.url = url


class AlreadySentResponse(Error):
  """The servlet already responded, no need to render a page template."""


class NoSuchPageException(Error):
  """The servlet finds that there is no page for the requested resource."""


class NoSuchProjectException(Error):
  """No project with the specified name exists."""


class NoSuchUserException(Error):
  """No user with the specified name exists."""


class TamperingException(Error):
  """The user edited a query param that we did not expect them to mess with."""


if __name__ == '__main__':
  sys.exit('This is not meant to be run as a standalone program. Exiting.')
