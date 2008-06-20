#! /usr/bin/env python
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
This file registers urls chat pages
"""

from twisted.python import log

from common import pageclasses
import framework.helpers
from chat import constants
from chat import chatpage


class PageSetup(framework.helpers.AbstractPageSetup):
    """This class configures the chat pages."""
  
    # TODO: we don't need dit_persist, but we might want a chat_persist
    def __init__(self, server, conn_pool,
               demetrius_persist, dit_persist, worktable, universal_ezt_data):
        self.server = server
        self.conn_pool = conn_pool
        self.demetrius_persist = demetrius_persist
        self.dit_persist = dit_persist
        self.worktable = worktable
        self.universal_ezt_data = universal_ezt_data.copy()

    def RegisterPages(self):
        
        log.msg("REGISTERING CHAT PAGE")
        chat_page = chatpage.ChatPage(
          self.conn_pool, self.demetrius_persist, self.universal_ezt_data)
        self._SetupProjectPage(
          chat_page.Handler, constants.CHAT_PAGE_URL)
        log.msg("CHAT PAGE READY")
