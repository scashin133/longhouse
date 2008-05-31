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

"""Class that implements the artifact update collision page.

This page is displayed only when one user views and edits an issue,
but another user has already submitted an issue update before the
first user submits his/her update.  It can also be shown when two
users attempt to edit the same download or wiki page at the same time.

TODO: give the user better options on how to proceed.
"""

import re

from ezt import ezt

from common import http

from framework import helpers

from demetrius import constants
from demetrius import pageclasses

_CONTINUE_URL_RE = re.compile(r'(issues/detail\?id=[0-9]+)'
                              '|(wiki/\w+)'
                              '|(downloads/detail\?name=[a-zA-Z0-9 \'"%]+)'
                              )

class ArtifactCollision(pageclasses.DemetriusPage):
  """ArtifactCollision page explains that a mid-air collision has occured."""

  _PAGE_TEMPLATE = 'framework/artifact-collision-page.ezt'
  _MAIN_TAB_MODE = constants.MAIN_TAB_NONE

  def GatherPageData(self, request, req_info):
    """Build up a dictionary of data values to use when rendering the page.

    Args:
      request: the HTTP request being processed.
      req_info: commonly used info parsed from the request.

    Returns: dict of values used by EZT for rendering the page.
    """

    artifact_name = req_info.GetParam('name')

    continue_url = req_info.GetParam('continue_url')
    if not _CONTINUE_URL_RE.match(continue_url):
       http.BadRequest(request)  # someone forged a link
       raise helpers.AlreadySentResponse()
    if req_info.project_name:
      artifact_detail_url = '/p/%s/%s' % (req_info.project_name, continue_url)
    else:
      artifact_detail_url = '/%s' % continue_url

    return {
      'artifact_name': artifact_name,
      'artifact_detail_url': artifact_detail_url,
      'show_project_nav': ezt.boolean(req_info.project_name),
      }
