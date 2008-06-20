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

from chat import irc_logbot
import chat.page_setup


def main(port, daemonized):
    """Creates the page objects (handlers) and starts the server."""
    
    
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
    
    chat_pages = chat.page_setup.PageSetup(
        server, conn_pool, demetrius_persist, dit_persist,
        worktable, template_data)
    chat_pages.RegisterPages()


    # These things need to be called after the twisted reactor is running
    
    server.callWhenRunning(demetrius_persist.GetAllUsers)
    
    server.callWhenRunning(demetrius_persist.GetAllProjects)
    
    server.callWhenRunning(irc_logbot.connect)


    server.run()

if __name__ == '__main__':
    print 'Run longhouse using the run script (run.py)'
