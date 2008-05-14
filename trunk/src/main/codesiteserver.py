#!/usr/bin/env python
#
# Copyright 2007 Google Inc. All Rights Reserved.

import sys

from twisted.web import server, resource, static
from twisted.internet import reactor
from twisted.python import log
from twisted.internet.error import CannotListenError

from demetrius.hostinghome import HostingHome
from demetrius.login import LoginPage

import resources

class CodesiteServer(object):

  def __init__(self, serviceport):
    self.port = serviceport
    self.root_resource = resources.RootResource()
    self.site = server.Site(self.root_resource)    
    

  def run(self):
      try:
          reactor.listenTCP(self.port, self.site)
      except CannotListenError:
          log.msg('Error: another process is already bound to port', self.port)
          sys.exit(1)
          
      reactor.run()

  def RegisterStaticFiles(self, relative_uri, path):
      
      # remove the leading '/', if any
      if relative_uri.startswith('/'):
          relative_uri = relative_uri[1:]
          
      self.root_resource.putChild(relative_uri, static.File(path))
      
  def RegisterHandler(self, relative_uri, callback, private=False,
                                does_write=None):
      self.root_resource.addHandler(relative_uri, callback)

  def RegisterPerProjectHandler(self, relative_uri, callback, private=False,
                                does_write=None):
    """Register a per-project handler.

    The relative_url should have a leading slash, and is relative to the
    project URL. For example, "/foo" to register a callback for the
    "/p/PROJECTNAME/foo" set of project URLs.

    callback and private are similar to RegisterHandler.
    """
    self.root_resource.addProjectHandler(relative_uri, callback)

  def RegisterPerUserHandler(self, relative_uri, callback, private=False):
    """Register a per-user page: e.g., "/u/USERNAME/".

    The parameters are similar to RegisterPerProjectHandler.
    """
    self.root_resource.addUserHandler(relative_uri, callback)
    
  def RegisterDeferred(self, relative_uri, callback):
      """ """
      self.root_resource.addDeferredHandler(relative_uri, callback)  
      
  def RegisterPerProjectDeferred(self, relative_uri, callback):
      """ """
      self.root_resource.addProjectDeferredHandler(relative_uri, callback) 
    
