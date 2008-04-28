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


"""Wrappers to isolate other code.google.com from pywrap*server dependencies.

See the function docstrings for more detail.
"""


# Symbolic constants for the HTTP status codes
HTTP_OK = 200
HTTP_MOVED_PERMANENTLY = 301
HTTP_FOUND = 302
HTTP_BAD_REQUEST = 400
HTTP_PERMISSION_DENIED = 403
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405
HTTP_INTERNAL_SERVER_ERROR = 500

HTTP_PROTO_POST = 'POST'


def HttpResponse(request, code=None):
  """Generate a response with a status code to an HTTP request.

  Args:
    request: HTTP request object
    code: optional HTTP status code; default is None (no status)
  """
  request.code = code


def SendRedirect(absolute_url, request, code=HTTP_MOVED_PERMANENTLY):
  """Send the 301/302 response code and write the Location: redirect"""
  request.headers['Location'] = absolute_url
  HttpResponse(request, code=code)


def BadRequest(request):
  """Generate a 400 (Bad Request) response.

  Args:
    request: HTTP request object
  """
  HttpResponse(request, code=HTTP_BAD_REQUEST)
