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

"""Classes to serve XML or JSON feeds with info about this project.

Summary of classes:
  ProjectMembersFeed: Provides a list of the members of a project.
"""

import sys

from demetrius import pageclasses
from demetrius import helpers


class ProjectMembersFeed(pageclasses.DemetriusPage):
  """XML and JSON feed describing all project labels."""

  _PAGE_TEMPLATE = 'demetrius/project-members-feed.ezt'

  def GatherPageData(self, request, req_info):
    """Gather info needed to generate the project members feed."""

    page_data = helpers.BuildProjectMembers(req_info.project, self.demetrius_persist, self.conn_pool)
    return page_data


if __name__ == '__main__':
  sys.exit('This is not meant to be run as a standalone program. Exiting.')
