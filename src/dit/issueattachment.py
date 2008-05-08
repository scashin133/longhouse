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

"""Demetrius Issue Tracker code to serve out issue attachments.
"""


from common import http

import framework.helpers

import dit.pageclasses
import dit.constants


class AttachmentPage(dit.pageclasses.DITPage):
  "AttachmentPage serves issue attachments."

  # Note that there is no _PAGE_TEMPLATE for this servlet, because we are not
  # generating an HTML page.

  def GatherPageData(self, request, req_info):
    """Parse the attachment ID from the request and serve its content.

    Args:
      request: the HTTP request being processed.
      req_info: commonly used info parsed from the request.

    Returns: dict of values used by EZT for rendering almost all DIT pages.
    """

    attachment_content = None

    aid = req_info.GetLongParam('aid')
    if aid is not None:
      attachment_content = self.dit_persist.GetIssueAttachmentContent(
        req_info.project_name, aid)

    if attachment_content is None:
      raise framework.helpers.NoSuchPageException()
    else:
      client_file_name = req_info.GetParam('name')
      if client_file_name:
        dispo = 'attachment; filename="%s"' % client_file_name
        request.output_headers().SetHeader('content-disposition', dispo, 1)

      request.SetContentType('application/octet-stream')
      if not client_file_name:
        http.BadRequest(request)
        # Don't try to do the normal page rendering
        raise framework.helpers.AlreadySentResponse('attachment content')

      request.output().WriteString(attachment_content.content())
      http.HttpResponse(request)
      # Don't try to do the normal page rendering
      raise framework.helpers.AlreadySentResponse('attachment content')
