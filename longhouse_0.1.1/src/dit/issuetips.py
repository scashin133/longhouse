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

"""A class to render a page of DIT search tips.
"""

import sys

from demetrius import constants
import dit.pageclasses


class IssueSearchTips(dit.pageclasses.DITPage):
  """IssueSearchTips on-line help on how to use issue search."""

  _PAGE_TEMPLATE = 'dit/issue-search-tips.ezt'
  _MAIN_TAB_MODE = constants.MAIN_TAB_ISSUES

  def GatherPageData(self, request, req_info):
    """Build up a dictionary of data values to use when rendering the page."""
    return {
      'issue_tab_mode': 'issueSearchTips'
      }


if __name__ == '__main__':
  sys.exit('This is not meant to be run as a standalone program. Exiting.')
