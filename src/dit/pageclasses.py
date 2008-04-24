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

"""DITPage extends DemetriusPage with DIT-specific details.

DITPage is th base class for all DIT web pages.  DIT pages work very
much like Demetrius pages, so this class does not modify much of the
behavior of DemetriusPage.  DITPage does add two additional instance
variables to hold references to the DIT-specific backend
interfaces. DITPage customizes the req_info class used to parse
requests, and makes some of that DIT-specific info available to EZT.
"""

from common import post
import demetrius.pageclasses
from dit import permissions


class DITPage(demetrius.pageclasses.DemetriusPage):
  """Base class for all DIT web pages.

  Defines a framework of methods that build up parts of the EZT
  context.
  """

  # Define a tool permission dictionary so that the RequestInfo object
  # will have DIT-specific permissions defined.
  _TOOL_PERMISSION_DICT = permissions.DIT_PERMISSIONS

  def __init__(self, conn_pool, demetrius_persist, dit_persist,
               universal_ezt_data, worktable=None):
    """Initialize this servlet so it can contact various backends later.

    Args:
      conn_pool: ConnectionPool object that interfaces to AuthSub.
      demetrius_persist: DemetriusPersist interface to storage backends.
      dit_persist: DITPersist interface to storage backends.
      universal_ezt_data: EZT data that is common to all pages.
      worktable: Worktable interface to a queue of pending backend tasks.
    """

    demetrius.pageclasses.DemetriusPage.__init__(
      self, conn_pool, demetrius_persist, universal_ezt_data,
      worktable=worktable)
    self.dit_persist = dit_persist

  def GatherBaseData(self, request, req_info):
    """Return a dict of info used on almost all pages.

    Args:
      request: the HTTP request being processed.
      req_info: commonly used info parsed from the request.

    Returns: dict of values used by EZT for rendering almost all DIT pages.
    """

    ezt_data = demetrius.pageclasses.DemetriusPage.GatherBaseData(
      self, request, req_info)

    dit_base_data = {
      # for issue-search-form.ezt, pagination, and the flipper
      'searchtip': '',
      'can': req_info.can,
      'query': req_info.query,
      'q': post.SafeForHTML(req_info.query),
      'colspec': None,
      'sortspec': post.SafeForHTML(req_info.sort_spec),

      'grid_x_attr': req_info.GetParam('x', ''),
      'grid_y_attr': req_info.GetParam('y', ''),
      'grid_cell_mode': req_info.GetParam('cells', 'tiles'),
      'grid_mode': None,
      }

    ezt_data.update(dit_base_data)
    return ezt_data
