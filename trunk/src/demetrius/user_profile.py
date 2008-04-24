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

"""A class to display the login page.
"""

import sys

from common import post
from common import http
from common import ezt_google

import framework.helpers

from demetrius import constants
from demetrius import pageclasses
from demetrius import helpers
from demetrius import permissions

class UserProfile(pageclasses.DemetriusPage):

    _PAGE_TEMPLATE = 'demetrius/user.ezt'
    
    def GatherPageData(self, request, req_info):
        self.viewed_user = None
        if req_info.viewed_user_id is not None:
            self.viewed_user = self.demetrius_persist.GetUser(req_info.viewed_user_id)
            if req_info.logged_in_user is not None:
                user_email = req_info.logged_in_user.email
                if user_email == self.viewed_user.account_email():
                    not_this_user = None
                    profile_username = req_info.logged_in_user.display_name
                else:
                    not_this_user = True
                    profile_username = self.viewed_user.account_email()
            else: 
                not_this_user = True
                profile_username = self.viewed_user.account_email()
        
        if self.viewed_user is not None:
            page_data = {
                'profile_username': profile_username,
                'not_this_user': not_this_user,
                'user_not_found': None,
                'viewed_user': self.viewed_user   
            }
        else:
            page_data = {
                       'user_not_found': 'true',
                       'profile_username': None,
                       'not_this_user': None,
                       'viewed_user': None
            }
        return page_data
        
if __name__ == '__main__':
  sys.exit('This is not meant to be run as a standalone program. Exiting.')