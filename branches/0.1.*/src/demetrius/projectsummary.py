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

"""A class to display the project summary page.
"""

import sys

from common import post

import framework.helpers

from demetrius import constants
from demetrius import pageclasses
from demetrius import helpers
from demetrius import permissions

class ProjectSummary(pageclasses.DemetriusPage):
  """ProjectSummary page shows brief description, members, and links."""

  _PAGE_TEMPLATE = 'demetrius/project-summary-page.ezt'
  _MAIN_TAB_MODE = constants.MAIN_TAB_SUMMARY

  def __init__(self, conn_pool, demetrius_persist, dit_persist,
               universal_ezt_data, worktable=None):
    pageclasses.DemetriusPage.__init__(
      self, conn_pool, demetrius_persist, universal_ezt_data,
      worktable=worktable)
    self.dit_persist = dit_persist
    #self._renderer = wikiformatter.WikiRenderer()
    self._renderer = None

  def EarlyPageProcessing(self, request, req_info):
    """Start getting some data while the user is being authenticated."""
    desc_blob_promise = self.MakePromise(
      self.demetrius_persist.GetProjectDescriptionCachedBlob,
      req_info.project_name)

    return desc_blob_promise

  def GatherPageData(self, request, req_info):
    """Build up a dictionary of data values to use when rendering the page."""
    page_data = helpers.BuildProjectMeta(req_info.project,
                                         self.demetrius_persist)
    member_promise = self.MakePromise(
        self._GatherMemberData, req_info)

    desc_blob_promise = req_info.early_promise
    description_pb = desc_blob_promise.WaitAndGetValue()
    description_promise = self.MakePromise(
      self._GatherProjectDescription, req_info, description_pb)

    page_data.update(member_promise.WaitAndGetValue())

    page_data.update(description_promise.WaitAndGetValue())

    links = helpers.BuildProjectLinks(req_info.project)
    page_data.update(links)

    return page_data

  def _GatherMemberData(self, req_info):
    """Asyncronous callback to gather part of the EZT page data."""
    return helpers.BuildProjectMembers(
      req_info.project, self.demetrius_persist,
      max_members_to_lookup=constants.MEMBERS_PER_PAGE)

  def _GatherProjectDescription(self, req_info, description_pb):
    """Asynchronous callback to gather part of the EZT page data."""
    # Compatibility. As long as existing project owners haven't
    # changed their description, their description is still rendered
    # as plaintext.
    return {
        'project_description':
        post.FormPlainTextToSafeHtml(req_info.project.description()),
        }


if __name__ == '__main__':
  sys.exit('This is not meant to be run as a standalone program. Exiting.')
