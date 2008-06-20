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

"""Classes for users to create a new project.

Summary of page classes:
  ProjectCreate: Displays a simple form asking for project info,
    and handles the form submission.
"""

import sys

from common import http
from common import post
from common import validate
from common import ezt_google

import framework.helpers
import framework.constants

from demetrius import constants
from demetrius import helpers
from demetrius import permissions
from demetrius import pageclasses
from demetrius import persist


class ProjectAdminPortal(pageclasses.DemetriusPage):
  """Portal page for project administration options.
  """

  _PAGE_TEMPLATE = 'demetrius/project-admin-portal.ezt'
  
  def AssertBasePermission(self, req_info):
    pageclasses.DemetriusPage.AssertBasePermission(self, req_info)
    # TODO: i18n error messages
    if not req_info.demetrius_perms.Check(permissions.EDIT_PROJECT):
        self.permission_error = 'You are not allowed to administer this project.'
        self.admin_tab_mode = None
        self.main_tab_mode = None
    else:
        self.admin_tab_mode = constants.ADMIN_TAB_PORTAL
        self.permission_error = None
        self.main_tab_mode = 't5'

  def GatherPageData(self, request, req_info):
      return {      
              'admin_tab_mode': self.admin_tab_mode,
              'main_tab_mode': self.main_tab_mode,
              'permission_error': self.permission_error
      }
  
  
if __name__ == '__main__':
  sys.exit('This is not meant to be run as a standalone program. Exiting.')
