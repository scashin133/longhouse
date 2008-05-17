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

"""
This program generates the pages for open source project hosting.  It
looks and works similar to what is seen on code.google.com.

This script uses HTTPServer.
"""

import os
import sys
import time
import random

from twisted.python import log
from twisted.internet import reactor

from main import codesiteserver

# Demetrius core and component classes
import framework.page_setup

import dit.page_setup
import dit.persist
import dit.constants

import demetrius.page_setup
import demetrius.persist
import demetrius.constants




def main(logging, logfile, port, daemonized):
    """Creates the page objects (handlers) and starts the server."""

    # make sure the storage folder and its subdirectories exist

    dirs = [
        'storage/unversioned',
        'storage/working_copies',
        'logs',
    ]
    
    for dir in dirs:
        try:
            os.makedirs(dir)
        except OSError:
            continue


    # start logging

    if logging:
        log.startLogging(open(logfile, "w+"), 0)
    
    if not daemonized:
        log.startLogging(sys.stdout)
    
    
    # Initialize the random seed.  Passing in None causes either the
    # system time or an OS-provided randomness source to be used when
    # seeing the random number generator.
    random.seed(None)

    # TODO(students): reimlpement this to set up a server using your technology choice.
    server = codesiteserver.CodesiteServer(port)

    ### Initialize infrastructure components

    # TODO(students): Do all start-up work, including connecting to
    # Subversion server and parsing certain persistent data.

    # We use this template data when expanding all of our EZT templates.
    template_data = {"banner_message" : None,
                 "read_only" : None,
                 "suggest_login_to_create" : None,
                 "title" : "Longhouse"}


    # TODO(students): replace this with your AuthSub object.
    conn_pool = None

    # TODO(students): replace this with your own asynchronous task manager.
    worktable = None
    
    dwiki_cache = None  # May be included in a future source code release.
    demetrius_persist = demetrius.persist.DemetriusPersist(dwiki_cache)
    dit_persist = dit.persist.DITPersist()
    dit_persist.register_demetrius_persist(demetrius_persist)
    #dit_persist = None

    """
    for i in range(6):
        username = "testuser" + str(i)
        demetrius_persist.CreateUser(username + "@gmail.com", username, "testpass")
    else:
        pass
    """
    
    
    #test_project = demetrius_persist.GetProject('testproject')
    #if test_project == None:
    #    print "couldn't load testproject from disk, creating it"
    #    demetrius_persist.CreateProject("testproject", [1], [2, 3, 4, 5], "This is the summary for the test project.",
    #        "http://www.google.com",
    #        "Now we must describe the test project.", ["label1", "label2", "label3"], "asf20", conn_pool)
    #    test_project = demetrius_persist.GetProject('testproject')
    #    test_project.set_repository_url('https://teamfreedom-projectcode.googlecode.com/svn/')
    #    test_project.set_persist_repository_url('svn://eastmont.no-ip.org/var/svn/shared/sean_longhouse_persist')
    #    test_project.set_persist_repository_username('longhouse')
    #    test_project.set_persist_repository_password('longhousepass')
    #    link = test_project.add_linksurl()
    #    link.set_url("http://www.google.com")
    #    link.set_label("Google label")
    #else:
    #    print 'loaded testproject from disk'


    # this causes an error because the reactor hasn't been started yet
    #test_project.setup_svn_controller()
    
    # demetrius_persist._StoreProject(test_project)


    framework_pages = framework.page_setup.PageSetup(
        server, conn_pool, demetrius_persist, dit_persist,
        worktable, template_data)
    framework_pages.RegisterPages()

    demetrius_pages = demetrius.page_setup.PageSetup(
        server, conn_pool, demetrius_persist, dit_persist,
        worktable, template_data)
    demetrius_pages.RegisterPages()

    dit_pages = dit.page_setup.PageSetup(
        server, conn_pool, demetrius_persist, dit_persist,
        worktable, template_data)
    dit_pages.RegisterPages()



    # load serialized users and projects    

    def load_from_saved_xml():
         demetrius_persist.GetAllUsers()
         demetrius_persist.GetAllProjects()

    log.msg('calling two methods after reactor is run')
    reactor.callLater(2, load_from_saved_xml)


    server.run()

if __name__ == '__main__':
    print 'Run longhouse using the run script (run.py)'
