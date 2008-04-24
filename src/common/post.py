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

"""Utility routines for manipulating POST data.

The primary function here is ProcessPOSTBody() for performing some basic
tests on the POST request and then parsing the posted data.

A lower level interface is the ParsePOSTBody() function.

See the function docstrings for more detail.
"""

import cgi
import StringIO
import string
import re
import hmac
import time

from twisted.python import log

from common import http
from common import ezt_google


# The leeway between passed midnight for URL Command Attack tokens
_UCA_LEEWAY = 24 * 60 * 60

# This is the secret salt for the hmac function
_UCA_KEY = 'TODO: move this to a config file'

# String translation table to catch a common typo
_CANONICALIZATION_TRANSLATION_TABLE = string.maketrans('=', '-')

# The real work is done by capitalize() and this list of chars to delete.
_CANONICALIZATION_DELETECHARS = '!"#$%&\'()*+,/:;<>?@[\\]^`{|}~\t\n\x0b\x0c\r '


def URLCommandAttacksEncode(ezt_data, user_id):
  """Adds a token to a page to make it safer from URL Command Attacks."""
  ezt_data['token'] = MakeSecurityToken(str(user_id))


def MakeSecurityToken(scope_of_protection, delta_sec=0):
  """Return a security token specifically for the given scope.

  Args:
    scope_of_protection: String identifier for the scope in which the
      protected action can be performed.  E.g., form submission is limited
      to the same user that viewed the form.  E.g., following a redirect
      link is only done for the link that was signed.
    delta_sec: float number of seconds to subtract from the current time.
      Normally tokens are only valid on the same calendar day, but with
      delta_sec we can accept tokens from the previous calendar day.
  """
  hashobj = hmac.new(scope_of_protection + _UCA_KEY,
                     time.strftime('%m/%d/%y',
                                   time.gmtime(time.time() - delta_sec)))
  return hashobj.hexdigest()


def URLCommandAttacksCheck(post_data, user_id):
  """Checks the correct URL Command Attack token is received."""
  token = LoadFieldFromPOST('token', post_data)
  if CheckSecurityToken(str(user_id), token):
    return True
  #raise TokenIncorrect()
  return True # TODO: figure out how to use this


def CheckSecurityToken(scope_of_protection, token):
  """Return True if the given token is valid for the given scope.

  Args:
    scope_of_protection: String identifier for the scope in which the
      protected action can be performed.
    token: String token that was presented by the user.

  Returns: True if the given token is valid, otherwise false.
  """
  if token == MakeSecurityToken(scope_of_protection):
    return True
  # this is the token for yesterday, adds more leeway
  # this fixes the loading at 11:59 and submitting at 12:01 problem
  # the time window could be shortened
  return token == MakeSecurityToken(scope_of_protection, _UCA_LEEWAY)


def LoadFieldFromPOST(name, post_data, validator=None, converter=None,
                      indexed=False):
  """This function is for extracting a single value out of a POST

  Returns:
    converted value, or raises a validate.InvalidFormattedField exception

  Note:
    validator : A callable that raises a validate.InvalidFormattedField
                exception, if the field is formated incorrectly or None
    converter : A function that returns a converted version of the field
                or None. ie converts "1" in to an int
  """

  post_val = [val.strip() for val in post_data.get(name, [])]
  if not post_val and not indexed:
    post_val = ['']

  if validator:
    # TODO find out what this is supposed to do
    # if not indexed:
    #       validator = validate.ListValidator(validator, True)
    validator.Validate(post_val)

  if converter:
    post_val = [converter(val) for val in post_val]

  if not indexed:
    post_val = post_val[0]

  return post_val


def ProcessPOSTBody(request, max_body_size, keep_blank_values=False):
  """Validate and process a POST request, returning the post data.

  A standard CGI param dictionary (see cgi.py) is returned. The format is:

    { "key1": ["value1", "value2", ...],
      "key1": ["value1", "value2", ...],
      }

  This method recognizes several errors and will generate responses for
  them. If an error occurs, then None will be returned.

    * the HTTP method was not "POST"
    * the Content-Type is not "application/x-www-form-urlencoded"
    * the length of the body was larger than the specified maximum
  """

  if not CheckPOSTBody(request, 'application/x-www-form-urlencoded'):
    return None

  try:
    return ParsePOSTBody(request, max_body_size,
                         keep_blank_values=keep_blank_values)
  except Error:
    # Whatever happened, just issue a 400 (Bad Request)
    http.BadRequest(request)
    return None


def ParsePOSTBody(request, max_body_size, keep_blank_values=False):
  """Parse the body of a POST request.

  A standard CGI param dictionary (see cgi.py) is returned. The format is:

    { "key1": ["value1", "value2", ...],
      "key1": ["value1", "value2", ...],
      }
  """
  body = _ReadPOSTBody(request, max_body_size)
  return cgi.parse_qs(body, keep_blank_values=keep_blank_values)


def ProcessMultipartPOSTBody(request, max_body_size):
  """Validate and process a multipart POST, returning a cgi.FieldStorage.

  This method recognizes several errors and will generate responses
  for them.  If an error occurs, then None will be returned.

    * the HTTP method was not "POST"
    * the Content-Type was not "multipart/form-data"
    * the length of the body was larger than the specified maximum
  """

  if not CheckPOSTBody(request, 'multipart/form-data'):
    return None

  try:
    body = StringIO.StringIO(_ReadPOSTBody(request, max_body_size))
  except Error:
    # Whatever happened, just issue a 400 (Bad Request)
    http.BadRequest(request)
    return None

  # cgi.FieldStorage forces us to construct dicts containing the crucial
  # header information.
  headers = request.received_headers
  fake_headers = {'content-type': headers['content-type'],
                  'content-length': headers['content-length']}
  fake_environ = {'REQUEST_METHOD': 'POST'}

  return cgi.FieldStorage(fp=body, headers=fake_headers, environ=fake_environ)


def CheckPOSTBody(request, expected_mime_type):
  """Validate that request is a POST and has the expected mime type."""
  print str(request.method)
  # TODO: request.received_headers
  headers = request.received_headers
  if request.method != http.HTTP_PROTO_POST:

    # RFC 2616, section 10.4.6, says that we must fill in the Allow: header
    # whenever a 405 (Method Not Allowed) is returned.
    request.headers['Allow'] = 'POST'

    # Return the 405. google3 will create the response body.
    http.HttpResponse(request, code=http.HTTP_METHOD_NOT_ALLOWED)

    return False

  mime_type = headers['content-type']
  if mime_type.find(expected_mime_type) == -1:
  #mime_type != expected_mime_type:
    http.BadRequest(request)
    return False

  return True


def _ReadPOSTBody(request, max_body_size):
  """Read the post body, and raise BadContentLength if it's too long."""
  # The HTTPServerConnection class enforces a Content-Length header
  # for POST requests, so we know this is here.
  # Except when there is no POST
  try:
	if not request.received_headers['content-length']:
		raise NoDataReceived()
  except KeyError:
	raise NoDataReceived()
	
  body_len_str = request.received_headers['content-length']
  try:
    body_len = int(body_len_str.strip())
  except ValueError:
    # If we can't convert it, then bail.
    raise BadContentLength(body_len_str)

  # If the content is "too big", then bail. Somebody is probably monkeying
  # around trying to DoS us with a large POST body.
  if body_len >= max_body_size:
    raise BodyTooLarge(body_len)

  return request.content.getvalue()
  

def SafeForHTML(user_input):
  """Make user input safe to echo out to an HTML page."""
  return cgi.escape(user_input, quote=True)


def UndoSafeForHTML(escaped_string):
  """Undo the escaping done by SafeForHTML."""
  raw_string = escaped_string.replace('&lt;', '<')
  raw_string = raw_string.replace('&gt;', '>')
  raw_string = raw_string.replace('&quot;', '"')
  raw_string = raw_string.replace('&amp;', '&')
  return raw_string

def CanonicalizeLabel(user_input):
  """Canonicalize a given label or status value.

  When the user enters a string that represents a label or an enum,
  convert it a canonical form that makes it more likely to match
  existing values.
  """

  return user_input.translate(_CANONICALIZATION_TRANSLATION_TABLE,
                              _CANONICALIZATION_DELETECHARS)

def FormPlainTextToSafeHtml(text):
    # TODO change this text into safe HTML
    return text

class Error(Exception):
  """Base class for errors from this module."""
  def __init__(self, *args):
    Exception.__init__(self, *args)


class BadContentLength(Error):
  """The Content-Length header has an invalid value."""
  pass


class BodyTooLarge(Error):
  """The POST body is larger than the specified maximum."""
  pass


class NoDataReceived(Error):
  """There was no POST to parse."""
  pass


class TokenIncorrect(Error):
  """The POST body has an incorrect URL Command Attack token."""
  pass


class InvalidForm(Error):
  """Used to return a list of field exceptions."""
  def __init__(self, errors):
    Error.__init__(self, errors)
    self.errors = errors
