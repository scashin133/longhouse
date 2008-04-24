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

"""A class to display the hosting home page.

Eventually, this will be generated periodically.
"""

import sys
import time

from ezt import ezt

from demetrius import constants
from demetrius import pageclasses

# This is the main tagline shown in the hosting page.
MAIN_TAGLINE = ('Release early, release often', 'We do',
                'release early release often')

# These taglines will be shown on certain days of each month, or the year.
ALT_TAGLINES = {
  '*/1': ('Adding people to a great project makes it greater',
          'Tip: inspire users to become contributors',
          'brooks law'),
  '*/6': ('A place for your stuff.c',
          'Tip: reuse, and be reusable',
          'http://www.google.com/codesearch'
          '?q=your+stuff+package:googlecode.com'),
  '*/11': ('Spend some quality time with your code',
           'Tip: schedule a testing sprint',
           'how to write test cases'),
  '*/16': ('Many hands make work light',
           'Tip: make it easy for contributors',
           'hackers guide'),
  '*/21': ('Nice idea, show me the code',
           'Tip: keep discussions concrete',
           ''),
  '*/26': ('Give the people what they want',
           'Tip: write down use cases',
           'how to write use cases'),

  '7/27': ('Greetings, programs!',
           'Hosting your code since 2006',
           'http://google-code-updates.blogspot.com/'
           '2006/08/project-hosting-r-us.html'),
  }


class HostingHome(pageclasses.DemetriusPage):
  """HostingHome shows the demetirus home page and link to create a project.

  This needs to be a full DemetriusPage rather than just a TemplatePage
  because we need to check permissions before offering the link to create
  a project.
  """

  _PAGE_TEMPLATE = 'demetrius/index.ezt'

  def GatherPageData(self, request, req_info):
    """Build up a dictionary of data values to use when rendering the page.

    Args:
      request: the HTTP request being processed.
      req_info: commonly used info parsed from the request.

    Returns: dict of values used by EZT for rendering almost all DIT pages.
    """

    # Choose a tagline based on today's date, or query string params.
    # The params are for testing, but they're safe if discovered by users.
    time_tuple = time.localtime()
    month = req_info.GetIntParam('m', time_tuple[1])
    day = req_info.GetIntParam('d', time_tuple[2])
    try:
      tagline_tuple = ALT_TAGLINES['%d/%d' % (month, day)]
    except KeyError:
      try:
        tagline_tuple = ALT_TAGLINES['*/%d' % day]
      except KeyError:
        tagline_tuple = MAIN_TAGLINE

    if tagline_tuple[2].startswith('http://'):
      tagline_href = tagline_tuple[2]
    elif tagline_tuple[2]:
      tagline_href = 'http://www.google.com/search?q=' + tagline_tuple[2]
    else:
      tagline_href = ''

    return {
      'tagline': tagline_tuple[0],
      'tagline_tip': tagline_tuple[1],
      'tagline_href': tagline_href,
      }


if __name__ == '__main__':
  sys.exit('This is not meant to be run as a standalone program. Exiting.')
