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

"""Some utility classes for interacting with EZT templates.

See the docstrings for more detail.
"""

import cStringIO
import os

from ezt import ezt
#from bo import BusinessObject

from common import http

_DISPLAY_VALUE_TRAILING_CHARS = 8
_DISPLAY_VALUETIP_CHARS = 120


class PBProxy(object):
  """Wraps a BusinessObject so it looks EZT friendly."""

  def __init__(self, pb):
    self.__pb = pb

  def __getattr__(self, name):
    """Make the getters EZT friendly.

    Psudo-hack alert: When attributes end with _bool, they are converted in
    to EZT style bools.
    ie if false they return 'None', if true they return 'true'
    """
    if name.endswith("_bool"):
      bool_name = name
      name = name[0:-5]
    else:
      bool_name = None

    # Make it possible for a PBProxy-local attribute to override the business
    # object field, or even to allow attributes to be added to the PBProxy that
    # the business object does not even have.
    if name in self.__dict__:
      if callable(self.__dict__[name]):
        val = self.__dict__[name]()
      else:
        val = self.__dict__[name]

      if bool_name:
        return ezt.boolean(val)
      return val

    if bool_name:
      # return a known _bool PB field proxy now, avoiding later processing
      return ezt.boolean(getattr(self.__pb, name)())

    val = getattr(self.__pb, name)()

    # Return a list of values which themselves have been wrapped in PBProxies.
    if isinstance(val, list):
      list_to_return = []
      for v in val:
        if isinstance(val, BusinessObject):
          list_to_return.append(PBProxy(v))
        else:
          list_to_return.append(str(v))
      return list_to_return

    return str(val)

  def DebugString(self):
    """Return a string represenation that is useful in debugging."""
    return 'PBProxy(%s)' % self.__pb


class GoogleTemplate(object):
  """An EZT Template with additional, Google-specific functionality.

  WriteResponse -- generate template output as a response.
  """

  def __init__(self, template_path, compress_whitespace=True,
               base_format=ezt.FORMAT_HTML):
    self.template_path = template_path
    # TODO(students): only true when developing UI changes, define a
    # command-line flag or configuration option to make prototyping
    # false when trying to run on a live site.
    self.prototyping = True
    self.template = None
    self.compress_whitespace = compress_whitespace
    self.base_format = base_format

  def WriteResponse(self, request, data, content_type=None):
    """Write the parsed and filled in template to http server."""

    response = self.GetResponse(data)
    
    # TODO: set content type (or do we need to?)
    if content_type:
      request.SetContentType(content_type)
    else:
        pass
      #request.SetContentTypeHTML()

    # Write out the response, log the request, and give a 200 response unless
    # otherwise specified.
    request.write(response)
    code = data.get('http_response_code', http.HTTP_OK)

    # Disable standard error reporting if requested in the passed dictionary
    disable_errors = data.get('disable_standard_errors', False)

    # TODO: respond with the correct http code
    #http.HttpResponse(request, code, disable_errors)

    # this will be used 9 times out of 10, but is helpful for caching
    return response

  def GetResponse(self, data):
    """Return the template with all the values parsed and filled in."""

    # We don't operate directly on self.template to avoid races.
    template = self.template
    if self.prototyping or template is None:
      template = ezt.Template(compress_whitespace=self.compress_whitespace)
      #template.parse(ezt.Reader(self.template_path),
      template.parse(ezt._FileReader(self.template_path),
                     base_format=self.base_format)
      if not self.prototyping:
        self.template = template

    str_io_buffer = cStringIO.StringIO()
    template.generate(str_io_buffer, data)
    return str_io_buffer.getvalue()

  def GetTemplatePath(self):
    """Accessor for the template path specified in the constructor.

      Returns:
        The string path for the template file provided to the constructor.
    """
    return self.template_path


class EZTError(object):
  """This class is a helper class to pass errors to EZT.

  This class is used to hold information that will be passed to EZT but might
  be unset. All unset values return None (ie EZT False)
  Example: page errors
  """
  def __getattr__(self, name):
    """This is the EZT retrieval function."""
    return None

  def AnyErrors(self):
    return len(self.__dict__) != 0

  def DebugString(self):
    return 'EZTError(%s)' % self.__dict__


def FitUnsafeText(text, length):
  """Trim some unsafe (unescaped) text to a specific length.

  Three periods are appended if trimming occurs. Note that we cannot use
  the ellipsis character (&hellip) because this is unescaped text.
  """
  if len(text) <= length:
    return text

  return text[:length] + '...'


def FitString(s, avail_space, max_trailing_chars=_DISPLAY_VALUE_TRAILING_CHARS,
              max_valuetip_chars=_DISPLAY_VALUETIP_CHARS):
  """Return a possibly shorter string that fits in the available space.

  If the string fits, return it for display as is.  If not, take out part of
  the middle, and provide a longer valuetip.

  Args:
    s: the string to be displayed.
    avail_space: the number of characters that will fit in the display area.

  Returns: (display_value, value_tip)
    display_value: the text to be displayed on the page.
    value_tip: more descriptive text for display when user hovers mouse.
  """

  _ELLIPS = '...'

  if len(s) <= avail_space: return s, ''
  leading_chars = s[:avail_space - max_trailing_chars]
  trailing_chars = s[- max_trailing_chars:]
  display_value = '%s%s%s' % (leading_chars, _ELLIPS, trailing_chars)
  value_tip = s[:max_valuetip_chars]
  if len(s) > max_valuetip_chars: value_tip += _ELLIPS
  return display_value, value_tip


def BytesKbOrMb(num_bytes):
  """Return a human-readable string representation of a number of bytes."""
  if num_bytes < 1024:
    return '%d bytes' % num_bytes  # e.g., 128 bytes
  if num_bytes < 99 * 1024:
    return '%.1f KB' % (num_bytes / 1024.0)  # e.g. 23.4 KB
  if num_bytes < 1024 * 1024:
    return '%d KB' % (num_bytes / 1024)  # e.g., 219 KB
  if num_bytes < 99 * 1024 * 1024:
    return '%.1f MB' % (num_bytes / 1024.0 / 1024.0)  # e.g., 21.9 MB
  return '%d MB' % (num_bytes / 1024 / 1024)  # e.g., 100 MB


class EZTItem(object):
  """A class that makes a collection of fields easily accessible in EZT."""

  def __init__(self, **kw):
    """Store all the given key-value pairs as fields of this object."""
    vars(self).update(kw)

  def __str__(self):
    return 'EZTItem(%s)' % str(vars(self))


def ljust(s, width):
  """Left-justify the given string, taking utf-8 encoding into account."""
  return s.decode('utf8', 'ignore').ljust(width).encode('utf8')
