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

"""Time-to-string and time-from-string routines.

Module Constants:
  TIME_TOTAL_RUN_FMT: LogElapsedTime() format string
  TIME_ELAPSED_FMT: LogElapsedTime() format string
  TIME_DEFAULT_INDENT: default number of LogElapsedTime() output indent columns
  TIME_DEFAULT_INDENT_MARK: default prefix for indented LogElapsedTime() output
"""

import os
import time
import commands


class Error(Exception):
  """Exception used to indicate problems with time routines"""
  pass

class TimeDecodeException(Error):
  """Exception used to indicate problems with date/time decoding"""
  pass


ISO_DATE_TIME_FMT = '%Y-%m-%d %H:%M:%S'

HTML_TIME_FMT = '%a, %d %b %Y %H:%M:%S GMT'


def TimeForHTMLHeader(when=None):
  """Return the given time (or now) in HTML header format."""
  if when is None:
    when = int(time.time())
  return time.strftime(HTML_TIME_FMT, time.gmtime(when))


def DateInSeconds(date, fmt=ISO_DATE_TIME_FMT):
  """Convert a date string into seconds from epoch.

  Args:
    date:  date string, in a format that matches that specified by the
      'fmt' argument
    fmt:  date format used by time.strptime(); default is '%Y-%m-%d %H:%M:%S'

  Returns:
    Date in seconds from epoch
  """
  # Set the daylight savings flag to -1 which will default
  # to the correct value for time.mktime.
  y, m, d, H, M, S, w, j, ds = time.strptime(date, fmt)
  return time.mktime((y, m, d, H, M, S, w, j, -1))


DATE_CMD_FMT = 'date -d"%s" +"%s"'

def DateStringFromEnglish(english, fmt=ISO_DATE_TIME_FMT):
  """Converts English relative time expression into a date/time string

  Arguments:
    english:  string containing relative expression of time in English
      (e.g. '2 days')
    fmt:  specifies format of date/time string; default is ISO
      YYYY-MM-DD HH:MM:SS

  Returns:
    date/time string formatted as specified by 'fmt'

  Raises:
    TimeDecodeException if an error occurred attempting to convert the English
    relative time expression string into a date/time string
  """
  status, output = commands.getstatusoutput(DATE_CMD_FMT % (english, fmt))

  if status:
    # external command had problems, so raise an exception
    if os.WIFEXITED(status):  status = os.WEXITSTATUS(status)
    raise TimeDecodeException('%d: %s' % (status, output))

  return output


def TimeInSecsFromEpoch(date_time, fmt=ISO_DATE_TIME_FMT):
  """Converts date/time string or English relative time to seconds from epoch

  Arguments:
    date_time:  date/time string or English time expression (e.g. '5 min')
      relative to the current time
    fmt:  specifies format of date/time string; default is ISO
      YYYY-MM-DD HH:MM:SS

  Returns:
    Time in seconds from epoch of the time represented by 'date_time'.

  Raises:
    TimeDecodeException if 'date_time' could not be converted using one of the
    available methods.
  """
  try:
    return DateInSeconds(date_time, fmt)
  except ValueError:
    # maybe date_time is an English relative time expression
    date_time = DateStringFromEnglish(date_time, fmt)

    try:
      # try to convert newly-created date/time string again (should succeed)
      return DateInSeconds(date_time, fmt)
    except ValueError, val_err:
      # something else is wrong, so raise an exception
      raise TimeDecodeException(str(val_err))


TIME_TOTAL_RUN_FMT = \
  "%(indent)stotal%(event_name)s run-time:  " \
  "%(hours)d:%(minutes)02d:%(seconds)02d"

TIME_ELAPSED_FMT = \
  "%(indent)selapsed%(event_name)s time so far:  " \
  "%(hours)d:%(minutes)02d:%(seconds)02d"

TIME_DEFAULT_INDENT = 1
TIME_DEFAULT_INDENT_MARK = '\n'

def SplitTimeInSeconds(time_in_seconds):
  """Splits a time in seconds into hours, minutes, and seconds

  Arguments:
    time_in_seconds: time in seconds to split

  Returns:
    (hours, minutes, seconds)
  """
  seconds = time_in_seconds // 1
  minutes = seconds // 60
  hours = minutes // 60
  seconds = seconds - (minutes * 60)
  minutes = minutes - (hours * 60)

  return hours, minutes, seconds


def GetTimeInSecondsAsString(time_in_seconds):
  """Converts a time in seconds into days/hours/minutes/seconds string

  Arguments:
    seconds: time in seconds

  Returns:
    shortest possible string of these parts:
      ? day(s) ? hour(s) ? minute(s) ? second(s)
  """
  hours, minutes, seconds = SplitTimeInSeconds(time_in_seconds)

  days = int(hours / 24)
  hours -= days * 24

  if days > 1:
    days_str = '%d days ' % days
  elif days == 1:
    days_str = '1 day '
  else:
    days_str = ''

  if hours > 1:
    hours_str = '%d hours ' % hours
  elif hours == 1:
    hours_str = '1 hour '
  else:
    hours_str = ''

  if minutes > 1:
    min_str = '%d minutes ' % minutes
  elif minutes == 1:
    min_str = '1 minute '
  else:
    min_str = ''

  if seconds > 1:
    sec_str = '%d seconds' % seconds
  elif seconds == 1:
    sec_str = '1 second'
  else:
    sec_str = ''

  out_str = days_str + hours_str + min_str + sec_str
  out_str = out_str.rstrip()

  if not out_str:
    out_str = '0 seconds'

  return out_str


def GetTimeDelayAsString(delay_in_seconds):
  """Converts a delay in seconds into 'after days/hours/minutes/seconds' string

  Argyments:
    delay_in_seconds: delay in seconds; 0 is 'immediately', None is 'never'

  Returns:
    None: 'never'
    0: 'immediately'
    others: 'after T', where T is a formatted time string
  """
  if delay_in_seconds is None:
    return 'never'

  if delay_in_seconds is 0:
    return 'immediately'

  return 'after %s' % GetTimeInSecondsAsString(delay_in_seconds)


def ComputeAbsoluteDate(timestamp):
  """Format timestamp like 'Sep 05', or 'Yesterday', or 'Today'."""

  now = int(time.time())
  delta = int(now - timestamp)
  delta_minutes = delta // 60
  delta_hours = delta_minutes // 60
  delta_days = delta_hours // 24
  if delta_days > 1:
    return time.strftime('%b %d', (time.localtime(timestamp)))
  if delta_days > 0:
    return 'Yesterday'
  return 'Today'


def ComputeRelativeDate(timestamp, recent_only=False):
  """Return a short string that makes timestamp more meaningful to the user.

  Describe the timestamp relative to the current time, e.g., '4
  hours ago'.  In cases where the timestamp is more than 6 days ago,
  we simply show the year, so that the combined absolute and
  relative parts look like 'Sep 05, 2005'.

  if recent_only is True, only return a description of recent relative
  dates.  Do not return the year, and do not put results inside parentheses.
  """

  now = int(time.time())
  delta = int(now - timestamp)
  d_minutes = delta // 60
  d_hours = d_minutes // 60
  d_days = d_hours // 24
  if recent_only:
    if d_days > 6: return ''
    if d_days > 1: return '%s days ago' % d_days # starts at 2 days
    if d_hours > 1: return '%s hours ago' % d_hours # starts at 2 hours
    if d_minutes > 1: return '%s minutes ago' % d_minutes
    if d_minutes > 0: return '1 minute ago'
    if delta > 0: return 'moments ago'
    return ''
  else:
    if d_days > 6: return ', %s' % (time.localtime(timestamp))[0]
    if d_days > 1: return ' (%s days ago)' % d_days # starts at 2 days
    if d_hours > 1: return ' (%s hours ago)' % d_hours # starts at 2 hours
    if d_minutes > 1: return ' (%s minutes ago)' % d_minutes
    if d_minutes > 0: return ' (1 minute ago)'
    if delta > 0: return ' (moments ago)'
    return ' (in the future)'


def GetInternetDateTimeString(timestamp):
  """Converts timestamp into Internet Date Time fmt (RFC 3336, ISO 8601)

  Args:
    timestamp: Seconds since the epoch in UTC.
  """

  return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(timestamp))


def GetCurrentInternetDateTimeString():
  """Converts current time into Internet Date Time fmt (RFC 3336, ISO 8601)"""

  return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
