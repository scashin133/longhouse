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

"""A class to display a paginated list of project owners and members.

For now, this page is only offered when a project has a huge
number of members.

In the future, this will list owners and members and members will be
able to add a brief textual description of their responsibilities in
the project.
"""

from framework import helpers
from framework import artifactlist

from demetrius import constants
from demetrius import pageclasses


class ProjectPeople(pageclasses.DemetriusPage):
  """ProjectMembers page shows a paginatied list of owners and members."""

  _PAGE_TEMPLATE = 'demetrius/project-people-page.ezt'
  _MAIN_TAB_MODE = constants.MAIN_TAB_SUMMARY

  def __init__(self, conn_pool, demetrius_persist,
               dit_persist, universal_ezt_data,
               worktable=None):
    pageclasses.DemetriusPage.__init__(
      self, conn_pool, demetrius_persist, universal_ezt_data,
      worktable=worktable)
    self.dit_persist = dit_persist

  def GatherPageData(self, request, req_info):
    """Build up a dictionary of data values to use when rendering the page."""
    all_members = req_info.project.member_ids_list()
    pagination = artifactlist.ArtifactPagination(
      req_info, all_members, constants.MEMBERS_PER_PAGE, 'people')

    # Only look up a limited number of users.
    cuis_by_id = self.conn_pool.GetClientUserInfoBatch(
      pagination.visible_results)
    member_proxies = [helpers.UserIDProxy(user_id, self.conn_pool,
                                          client_user_info=cuis_by_id[user_id])
                      for user_id in pagination.visible_results]

    return {
      'members': member_proxies,
      'pagination': pagination,
      }
