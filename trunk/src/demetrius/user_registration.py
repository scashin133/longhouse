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

"""A class to allow users to register a new account.

A new user will supply their email address and their password
(password supplied twice, for validation purposes.)
Then they will have to go to their email, find an email that Longhouse
sends to their inbox to verify their registration."""

import sys

from common import post
from common import http
from common import ezt_google

import framework.helpers

from demetrius import constants
from demetrius import pageclasses
from demetrius import helpers
from demetrius import permissions

class UserRegistration(pageclasses.DemetriusPage):
  """Shows a page with a simple form to create an account.
  """

  _PAGE_TEMPLATE = 'demetrius/register.ezt'
  
  def GatherPageData(self, request, req_info):
    """Build up a dictionary of data values to use when rendering the page."""
    if (req_info.GetParam('email_address')) is None:
        email_address = ''
    else:
        email_address = req_info.GetParam('email_address')
        
    page_data = {
                 'email_address': email_address,
                 'errors': req_info.errors or ezt_google.EZTError(),
                 }
    return page_data
  
  def ProcessForm(self, request, req_info):
      """The method called when the user submits the registration request."""
      
      errors = ezt_google.EZTError()
      post_data = post.ParsePOSTBody(request, framework.constants.MAX_POST_BODY_SIZE)
      
      email_address = None
      password1 = None
      password2 = None
      
      try:
          email_address = post.LoadFieldFromPOST('email_address', post_data)
      except validate.InvalidFormattedField, e:
          errors.email_address = 'Invalid email address.'
      
      if not '@' in email_address:
          errors.email_address = 'Invalid email address. This field should take the form of name@domain.ext'
      
      try:
          password1 = post.LoadFieldFromPOST('password1', post_data)
      except validate.InvalidFormattedField, e:
          errors.password1 = 'Invalid entry for first password field'
      
      try:
          password2 = post.LoadFieldFromPOST('password2', post_data)
      except validate.InvalidFormattedField, e:
          errors.password2 = 'Invalid entry for second password field'
      
      existing_user_id = self.demetrius_persist.CheckIfEmailAddressIsTaken(email_address)
      
      if existing_user_id is not None:
          errors.email_address = 'Sorry, that email address is already registered as an account.'
          
      if password1 == '':
          errors.password1 = 'Sorry, your password can\'t be blank.'
      
      if password2 == '':
          errors.password2 = 'Sorry, your password can\'t be blank.'
      
      if password1 != password2:
          errors.other_error = 'Sorry, your two password entries don\'t match. Please try again - matching the two entries helps make sure that you know what your password is.'
            
      if not errors.AnyErrors():
          self.demetrius_persist.CreateUser(email_address, email_address, password1, True)
          uid = self.demetrius_persist.LookupUserIdByEmail(email_address)
          request.getSession().logged_in_user_id = uid
          url = framework.helpers.FormatAbsoluteURL(
                        None, constants.HOSTING_HOME_URL, request)
          http.SendRedirect(url, request)
      
      if errors.AnyErrors():
          errors.any_errors = True
          req_info.PrepareForSubrequest(None, errors, email_address=email_address)
          self.Handler(request, req_info=req_info)
          return


      
if __name__ == '__main__':
    sys.exit('This is not meant to be run as a standalone program. Exiting.')
        