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

"""Classes that implement the advanced search feature of DIT.

The advanced search page simply displays an HTML page with a form.
The form handler converts the widget-based query into a googley query
string and redirects the user to the issue list servlet.
"""

from common import http
from common import post

import framework.helpers
import framework.constants

import demetrius.constants

import dit.pageclasses
import dit.constants

class IssueAdvancedSearch(dit.pageclasses.DITPage):
  """IssueAdvancedSearch shows a form to enter an advanced search."""

  _PAGE_TEMPLATE = 'dit/issue-advsearch-page.ezt'
  _MAIN_TAB_MODE = demetrius.constants.MAIN_TAB_ISSUES

  def GatherPageData(self, request, req_info):
    """Build up a dictionary of data values to use when rendering the page.

    Args:
      request: the HTTP request being processed.
      req_info: commonly used info parsed from the request.

    Returns: dict of values used by EZT for rendering almost all DIT pages.
    """

    return {
      'issue_tab_mode': 'issueAdvSearch'
      }


  def ProcessForm(self, request, req_info):
    """Process a posted advanced query form.

    Args:
      request: the HTTP request being processed.
      req_info: commonly used info parsed from the request.
    """

    post_data = post.ProcessPOSTBody(
        request, framework.constants.MAX_POST_BODY_SIZE)
    if post_data is None:
      # An error occurred and the response was generated. We're done.
      return

    can =  2  # Default to searching open issues in this project.
    if 'can' in post_data: can = post_data['can'][0]

    terms = []
    self._AccumulateANDTerm('', 'words', post_data, terms)
    self._AccumulateANDTerm('-', 'without', post_data, terms)
    self._AccumulateANDTerm('label:', 'labels', post_data, terms)
    self._AccumulateORTerm('status:', 'statuses', post_data, terms)
    self._AccumulateORTerm('reporter:', 'reporters', post_data, terms)
    self._AccumulateORTerm('owner:', 'owners', post_data, terms)
    self._AccumulateORTerm('cc:', 'cc', post_data, terms)
    self._AccumulateORTerm('commentby:', 'commentby', post_data, terms)

    if 'starcount' in post_data:
      starcount = int(post_data['starcount'][0])
      if starcount >= 0:
        terms.append('starcount:%s' % starcount)

    url = framework.helpers.FormatAbsoluteURL(
      req_info, dit.constants.ISSUE_LIST_PAGE_URL, request,
      q=' '.join(terms), can=can)
    http.SendRedirect(url, request)

  def _AccumulateANDTerm(self, operator, form_field, post_data, search_query):
    """Build a query that matches issues with ALL of the given field values."""
    if form_field in post_data:
      user_input = post_data[form_field][0]
      values = dit.constants.TERM_RE.findall(user_input)
      search_terms = ['%s%s' % (operator, v) for v in values]
      search_query.extend(search_terms)

  def _AccumulateORTerm(self, operator, form_field, post_data, search_query):
    """Build a query that matches issues with ANY of the given field values."""
    if form_field in post_data:
      user_input = post_data[form_field][0]
      values = dit.constants.TERM_RE.findall(user_input)
      search_term = '%s%s' % (operator, ','.join(values))
      search_query.append(search_term)
