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

class UserValidation(pageclasses.DemetriusPage):
  """Shows a page with a simple form to validate an account.
  """

  _PAGE_TEMPLATE = 'demetrius/validate.ezt'
  
  def GatherPageData(self, request, req_info):
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
      
      print 'entered ProcessForm'
      
      errors = ezt_google.EZTError()
      post_data = post.ParsePOSTBody(request, framework.constants.MAX_POST_BODY_SIZE)
      
      email_address = None
      validatekey = None
      
      try:
          email_address = post.LoadFieldFromPOST('email_address', post_data)
      except validate.InvalidFormattedField, e:
          errors.email_address = 'Invalid entry for email address.'
      
      if not '@' in email_address:
          errors.email_address = 'Invalid email address. This field should take the form of name@domain.ext'       
   
      existing_user_id = self.demetrius_persist.CheckIfEmailAddressIsTaken(email_address)
      
      if existing_user_id is None:
          errors.email_address = 'Sorry, that email address isn\'t registered as an account.'

      try:
          validatekey = post.LoadFieldFromPOST('validatekey', post_data)
      except validate.InvalidFormattedField, e:
          errors.validatekey = 'Invalid format for validation key.'
         
      if not errors.AnyErrors():
          validation_result = self.demetrius_persist.ValidateNewUserKey(email_address, validatekey)
          if validation_result == 'validated':
              url = framework.helpers.FormatAbsoluteURL(
                        None, constants.HOSTING_HOME_URL, request)
              http.SendRedirect(url, request)
          elif validation_result == 'invalid key':
            errors.validatekey = 'Incorrect validation key. Check your e-mail to make sure that you\'re entering the key correctly.'
      
      if errors.AnyErrors():
          errors.any_errors = True
          req_info.PrepareForSubrequest(None, errors, email_address=email_address)
          self.Handler(request, req_info=req_info)
          return
  
if __name__ == '__main__':
    sys.exit('This is not meant to be run as a standalone program. Exiting.')
        