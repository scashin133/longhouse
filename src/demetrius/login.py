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

class LoginPage(pageclasses.DemetriusPage):

    _PAGE_TEMPLATE = 'demetrius/login.ezt'
          
    def GatherPageData(self, request, req_info):
        """Build up a dictionary of data values to use when rendering the page."""

        if(req_info.GetParam('followup')) is None:
            url_continue = ''
        else:
            url_continue = req_info.GetParam('followup')
        
        if (req_info.GetParam('username')) is None:
            username = ''
        else:
            username = req_info.GetParam('username')
        
        if (req_info.GetParam('error')) is None:
            error = ''
        else:
            error = req_info.GetParam('error')
        
        page_data = {
                     'username': username,
                     'errors': req_info.errors or ezt_google.EZTError(),
                     'error': error,
                     'followup_page': url_continue
                     }
        return page_data

    def ProcessForm(self, request, req_info):

        errors = ezt_google.EZTError()
        post_data = post.ParsePOSTBody(request, framework.constants.MAX_POST_BODY_SIZE)
        #post.URLCommandAttacksCheck(post_data, req_info.logged_in_user_id)

        # get post data

        try:
            username = post.LoadFieldFromPOST('username', post_data)
        except validate.InvalidFormattedField, e:
            errors.username = e.text
            username = post.LoadFieldFromPOST('username', post_data)

        # TODO: incoming password should be hashed, LoadFieldFromPOST('pwhash'
        # let's leave it plaintext for the Dec 6 demo
        try:
            pwhash = post.LoadFieldFromPOST('password', post_data)
        except validate.InvalidFormattedField, e:
            errors.pwhash = e.text
            pwhash = post.LoadFieldFromPOST('password', post_data)
        
        try:
            redirect = post.LoadFieldFromPOST('followup_page', post_data)
            #if redirect == '':
            #   redirect = constants.HOSTING_HOME_URL
            redirect = constants.HOSTING_HOME_URL
        except validate.InvalidFormattedField, e:
            redirect = constants.HOSTING_HOME_URL
        
        # validate user name
        # if user name exists, log the user in if password is correct
        # if user name exists and password isn't correct, or the 
        # user name doesn't exist, redirect back to the login page
        # with the error
        uid = None
        if not errors.AnyErrors():
            uid = self.demetrius_persist.LookupUserIdByEmail(username)
            if not uid is None:
                user_pb = self.demetrius_persist.GetUser(uid)
                if user_pb.verify_account_password(pwhash) is True:
                    # successful login. add their user_id to the sessions
                    request.getSession().logged_in_user_id = uid
                    # TODO: redirect them to where they were before they logged in
                    url = framework.helpers.FormatAbsoluteURL(
                        None, redirect, request)
                    http.SendRedirect(url, request)
                else:
                    url = framework.helpers.FormatAbsoluteURL(
                        None, constants.LOGIN_PAGE_URL, request, username=username, redirect=redirect, error='Invalid username/password combination.')
                    http.SendRedirect(url, request)
            else:
                url = framework.helpers.FormatAbsoluteURL(
                        None, constants.LOGIN_PAGE_URL, request, username=username, redirect=redirect, error='That email address doesn\'t exist as a user. Be sure to use your full email address.')
                http.SendRedirect(url, request)
        
        # this if statement SHOULD take effect if
        # the user navigates to the page alone, i.e.,
        # without using POST from the login form
        
        if errors.AnyErrors():
            url = framework.helpers.FormatAbsoluteURL(
                        None, constants.LOGIN_PAGE_URL, request);
            http.SendRedirect(url, request)    

        

  
if __name__ == '__main__':
    sys.exit('This is not meant to be run as a standalone program. Exiting.')
