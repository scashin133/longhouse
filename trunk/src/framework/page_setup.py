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

"""Sets up the urls for Framework pages. And relevant utility functions.

The framework servlets present demetrius-wide concepts to end-users.
E.g., if two users try to edit the same artifact at the same time.
"""

import sys

from twisted.python import log

from framework import constants
from framework import helpers
from framework import artifactcollision
from framework import svncontrols

class PageSetup(helpers.AbstractPageSetup):
  """This class configures the Demetrius URLs."""

  def __init__(self, server, conn_pool,
               demetrius_persist, dit_persist,
               worktable, universal_ezt_data):
    self.server = server
    self.conn_pool = conn_pool
    self.demetrius_persist = demetrius_persist
    self.dit_persist = dit_persist
    self.worktable = worktable
    self.universal_ezt_data = universal_ezt_data.copy()

  def RegisterPages(self):
    """Register all the framework pages, forms, and feeds with the server."""

    # Collisions can happen on artifacts within a project, or outside.
    artifact_collision_page = artifactcollision.ArtifactCollision(
      self.conn_pool, self.demetrius_persist,
      self.universal_ezt_data)
    self._SetupProjectPage(artifact_collision_page.Handler,
                           constants.ARTIFACT_COLLISION_PAGE_URL)
    self._SetupSitePage(artifact_collision_page.Handler,
                        constants.NONPROJECT_COLLISION_PAGE_URL)

    self._SetupDeferredPage(svncontrols.deferred_helloworld, '/test/hello')

    projectSvnUpPage = svncontrols.ProjectSvnUpPage(self.demetrius_persist)
    self._SetupPerProjectDeferredPage(projectSvnUpPage.Handler, '/svnup')

    """
    excessive_activity_page = excessiveactivity.ExcessiveActivity(
      self.conn_pool, self.demetrius_persist,
      self.universal_ezt_data)
    self._SetupSitePage(excessive_activity_page.Handler,
                        constants.EXCESSIVE_ACTIVITY_PAGE_URL)
    """

    log.msg('Finished registering framework handlers.')

if __name__ == '__main__':
  sys.exit('This is not meant to be run as a standalone program. Exiting.')
