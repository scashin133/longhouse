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

"""Implemention of the issue list feature of the Demetrius Issue Tracker.
"""

from ezt import ezt

from twisted.python import log

from common import post
from common import ezt_google
from common import timestr

from framework import artifactlist
import framework.helpers
import framework.constants

import demetrius.helpers
import demetrius.constants
import demetrius.permissions

import dit.helpers
import dit.pageclasses
import dit.constants


class IssueList(dit.pageclasses.DITPage):
  """IssueList shows a page with a list of issues (search results).

  The issue list is actually a table with a configurable set of columns
  that can be edited by the user.
  """

  _PAGE_TEMPLATE = 'dit/issue-list-page.ezt'
  _MAIN_TAB_MODE = demetrius.constants.MAIN_TAB_ISSUES

  def _GetEarlyData(self, request, req_info):
    """Retrieve the project issue config and issues that match the query."""
    config = self.dit_persist.GetProjectConfig(req_info.project_name)
    return config

  def EarlyPageProcessing(self, request, req_info):
    """Start getting some data while the user is being authenticated."""
    return self.MakePromise(self._GetEarlyData, request, req_info)

  def GatherPageData(self, request, req_info):
    """Build up a dictionary of data values to use when rendering the page.

    Args:
      request: the HTTP request being processed.
      req_info: commonly used info parsed from the request.

    Returns: dict of values used by EZT for rendering almost all DIT pages.
    """

    config = req_info.early_promise.WaitAndGetValue()

    results = dit.helpers.SearchIssues(req_info, self.dit_persist, config)

    # Check if the user's query is just the ID of an existing issue.
    if dit.constants.JUMP_RE.match(req_info.query):
      issue_id = int(req_info.query)
      issue, ts = self.dit_persist.GetIssue(req_info.project_name, issue_id)

      if issue is not None:
        url = framework.helpers.FormatAbsoluteURL(
          req_info, dit.constants.ISSUE_DETAIL_PAGE_URL, request,
          id=issue_id)
        raise framework.helpers.RedirectException('jumping to issue', url)

    col_spec = artifactlist.GetColSpec(
      req_info, config, dit.constants.DEFAULT_COL_SPEC)
    columns = col_spec.split()
    lower_columns = col_spec.lower().split()

    allowed_results = self._FilterOutPrivateIssues(
      req_info.logged_in_user_id, req_info.demetrius_perms, results)

    pagination = artifactlist.ArtifactPagination(
      req_info, allowed_results, dit.constants.DEFAULT_RESULTS_PER_PAGE,
      dit.constants.ISSUE_LIST_PAGE_URL)

    star_promise = self.MakePromise(
      self._GetStarredIssues, req_info)

    issue_participant_ids = {}
    for issue in allowed_results:
      issue_participant_ids[issue.owner_id()] = True
      for cc_id in issue.cc_ids_list():
        issue_participant_ids[cc_id] = True
    proxies_by_id = framework.helpers.MakeAllUserIDProxies(
      self.conn_pool, self.demetrius_persist, issue_participant_ids.keys())

    starred_issues = star_promise.WaitAndGetValue()

    table_data = []
    grid_data = []
    grid_x_attr = req_info.GetParam('x', config.default_x_attr() or '').lower()
    grid_x_headings = ['All']
    grid_y_attr = req_info.GetParam('y', config.default_y_attr() or '').lower()
    grid_y_headings = ['All']
    grid_mode = req_info.GetParam('mode', 'list') == 'grid'
    if not grid_mode:
      table_data = self._MakeTableData(
        pagination.visible_results, req_info.logged_in_user_id,
        starred_issues, lower_columns, proxies_by_id)
    else:
      all_label_values = {}
      for art in allowed_results:
        all_label_values[art.id()], unused = artifactlist.MakeLabelValuesDict(art)

      if grid_x_attr:
        grid_x_items = artifactlist.ExtractUniqueValues(
          [grid_x_attr], allowed_results, proxies_by_id)
        grid_x_headings = grid_x_items[0].filter_values
        if artifactlist.AnyArtifactHasNoAttr(allowed_results, grid_x_attr,
                                             proxies_by_id, all_label_values):
          grid_x_headings.append(framework.constants.NO_VALUES)
          grid_x_headings.sort()
      if grid_y_attr:
        grid_y_items = artifactlist.ExtractUniqueValues(
          [grid_y_attr], allowed_results, proxies_by_id)
        grid_y_headings = grid_y_items[0].filter_values
        if artifactlist.AnyArtifactHasNoAttr(allowed_results, grid_y_attr,
                                             proxies_by_id, all_label_values):
          grid_y_headings.append(framework.constants.NO_VALUES)
          grid_y_headings.sort()
      log.msg('grid_x_headings = %s' % grid_x_headings)
      log.msg('grid_y_headings = %s' % grid_y_headings)
      grid_data = self._MakeGridData(
        allowed_results, req_info.logged_in_user_id,
        starred_issues, grid_x_attr, grid_x_headings,
        grid_y_attr, grid_y_headings, proxies_by_id, all_label_values)

    # We need ordered_columns because EZT loops have no loop-counter available.
    # And, we use column number in the Javascript to hide/show columns.
    ordered_columns = [ezt_google.EZTItem(col_index=i, name=columns[i])
                       for i in range(len(columns))]

    # Used to offer easy filtering of each unique value in each column.
    column_values = artifactlist.ExtractUniqueValues(
      lower_columns, allowed_results, proxies_by_id)

    # We show a special message when no query will every produce any results
    # because the project has no issues in it.
    project_has_any_issues = True
    if not results:
      if self.dit_persist.GetCurrentIssueId(
        req_info.project_name, self.demetrius_persist) == 1:
        project_has_any_issues = False

    unshown_columns = artifactlist.ComputeUnshownColumns(
        allowed_results, columns, dit.constants.DEFAULT_COL_SPEC.split(),
        dit.constants.OTHER_BUILT_IN_COLS)

    grid_axis_choice_dict = {}
    for oc in ordered_columns:
      grid_axis_choice_dict[oc.name] = True
    for uc in unshown_columns:
      grid_axis_choice_dict[uc] = True
    for bad_axis in ['Summary', 'ID', 'Opened']:
      if bad_axis in grid_axis_choice_dict:
        del grid_axis_choice_dict[bad_axis]
    grid_axis_choices = grid_axis_choice_dict.keys()
    grid_axis_choices.sort()

    return {
      'ordered_columns': ordered_columns,
      'unshown_columns': unshown_columns,
      'table_data': table_data,
      'column_values': column_values,
      'issue_tab_mode': 'issueList',
      'pagination': pagination,
      'results': results,  # Really only useful in if-any.
      'project_has_any_issues': ezt.boolean(project_has_any_issues),
      'colspec': post.SafeForHTML(col_spec),
      'default_colspec': dit.constants.DEFAULT_COL_SPEC,
      'default_results_per_page': dit.constants.DEFAULT_RESULTS_PER_PAGE,

      'grid_mode': ezt.boolean(grid_mode),
      'grid_x_attr': grid_x_attr,
      'grid_x_headings': grid_x_headings,
      'grid_y_attr': grid_y_attr,
      'grid_y_headings': grid_y_headings,
      'grid_data': grid_data,
      'grid_axis_choices': grid_axis_choices,
      'grid_cell_mode': req_info.GetParam('cells', 'tiles'),
    }

  def _MakeTableData(self, visible_results, logged_in_user_id, starred_issues,
                     lower_columns, proxies_by_id):
    """Return a list of list row objects for display by EZT."""
    table_data = []
    cell_factories = [_CELL_FACTORIES.get(col, artifactlist.TableCellKeyLabels)
                      for col in lower_columns]
    for r in visible_results:
      if r.owner_id() == logged_in_user_id:
        owner_is_me = True
      else:
        owner_is_me = False
      row = _MakeRowData(r, lower_columns, owner_is_me, proxies_by_id,
                         cell_factories)
      row.issue_id = r.id()
      row.starred = ezt.boolean(r.id() in starred_issues)
      table_data.append(row)
    return table_data

  def _MakeGridData(self, allowed_results, logged_in_user_id,
                    starred_issues, x_attr, grid_col_values,
                    y_attr, grid_row_values, proxies_by_id, all_label_values):
    """Return all data needed for EZT to render the body of the grid view."""
    def IssueProxyFactory(issue_pb):
      return dit.helpers.IssuePBProxy(issue_pb, self.conn_pool, proxies_by_id)

    grid_data = artifactlist.MakeGridData(
      allowed_results, x_attr, grid_col_values, y_attr, grid_row_values,
      proxies_by_id, IssueProxyFactory, all_label_values)
    for grid_row in grid_data:
      for grid_cell in grid_row.cells_in_row:
        for tile in grid_cell.tiles:
          tile.starred = ezt.boolean(int(tile.id) in starred_issues)
    return grid_data

  def _FilterOutPrivateIssues(self, user_id, perms, issues):
    """Return a filtered list of issues that the user can view."""
    return [issue for issue in issues
            if demetrius.permissions.CanView(
              user_id, perms, issue, issue.reporter_id())]

  def _GetStarredIssues(self, req_info):
    """Get the list of issues that the logged in user has starred."""
    userissuestars = self.dit_persist.GetUserIssueStars(
      req_info.project_name, req_info.logged_in_user_id)
    return userissuestars.issue_ids_list()


def _MakeRowData(issue, columns, owner_is_me, proxies_by_id, cell_factories):
  """Make a TableRow for use by EZT when rendering HTML table of results.

  Args:
    issue: an instance of dit_pb.Issue
    columns: list of lower-case column names
    owner_is_me: boolean indicating that the logged in user is the owner
      of the current issue
    proxies_by_id: dictionary of "proxies" having a "display_name" member.
    cell_factories: list of functions that each create TableCell
      objects for a given column.
  """
  ordered_row_data = []
  non_col_labels = []
  label_values = {}

  # Group all "Key-Value" labels by key, and separate the "OneWord" labels.
  for label_name in issue.labels_list():
    in_column = False
    if '-' in label_name:
      column_name, value = label_name.split('-', 1)
      column_name = column_name.lower()
      if column_name in columns:
        if column_name not in label_values: label_values[column_name] = []
        label_values[column_name].append(value)
        in_column = True
    if not in_column and '-' not in label_name:
      non_col_labels.append(label_name)

  # Build up a list of TableCell objects for this row.
  for i in range(len(columns)):
    col = columns[i]
    factory = cell_factories[i]
    new_cell = factory(issue, col, proxies_by_id, non_col_labels, label_values)
    new_cell.col_index = i
    ordered_row_data.append(new_cell)

  return artifactlist.TableRow(ordered_row_data, owner_is_me)


class TableCellID(artifactlist.TableCell):
  """TableCell subclass specifically for showing issue IDs."""
  def __init__(self, issue, col, proxies_by_id, non_col_labels, label_values):
    self.type = artifactlist.CELL_TYPE_ID


class TableCellSummary(artifactlist.TableCell):
  """TableCell subclass specifically for showing issue summaries."""
  def __init__(self, issue, col, proxies_by_id, non_col_labels, label_values):
    self.type = artifactlist.CELL_TYPE_SUMMARY
    self.value = issue.summary()
    if not issue.summary_is_escaped():
      self.value = post.SafeForHTML(self.value)
    self.non_column_labels = non_col_labels


class TableCellStatus(artifactlist.TableCell):
  """TableCell subclass specifically for showing issue status values."""
  def __init__(self, issue, col, proxies_by_id, non_col_labels, label_values):
    self.type = artifactlist.CELL_TYPE_ATTR
    self.value = issue.status()
    if not self.value:
      self.value = framework.constants.NO_VALUES


class TableCellOwner(artifactlist.TableCell):
  """TableCell subclass specifically for showing issue owner name."""
  def __init__(self, issue, col, proxies_by_id, non_col_labels, label_values):
    self.type = artifactlist.CELL_TYPE_ATTR
    if not issue.has_owner_id():
      self.value = framework.constants.NO_VALUES
    else:
      self.value = proxies_by_id[issue.owner_id()].display_name

class TableCellStars(artifactlist.TableCell):
  """TableCell subclass specifically for showing issue star count."""
  def __init__(self, issue, col, proxies_by_id, non_col_labels, label_values):
    self.type = artifactlist.CELL_TYPE_ATTR
    self.value = issue.star_count()


class TableCellOpened(artifactlist.TableCell):
  """TableCell subclass specifically for showing issue opened date."""
  def __init__(self, issue, col, proxies_by_id, non_col_labels, label_values):
    self.type = artifactlist.CELL_TYPE_UNFILTERABLE
    self.value = timestr.ComputeRelativeDate(
        issue.opened_timestamp(), recent_only=True)
    if not self.value:
      self.value = timestr.ComputeAbsoluteDate(issue.opened_timestamp())


class TableCellClosed(artifactlist.TableCell):
  """TableCell subclass specifically for showing issue closed date."""
  def __init__(self, r, col, proxies_by_id, non_col_labels, label_values):
    self.type = artifactlist.CELL_TYPE_UNFILTERABLE
    self.value = framework.constants.NO_VALUES
    if r.has_closed_timestamp():
      self.value = timestr.ComputeRelativeDate(
          r.closed_timestamp(), recent_only=True)
      if not self.value:
        self.value = timestr.ComputeAbsoluteDate(r.closed_timestamp())


class TableCellModified(artifactlist.TableCell):
  """TableCell subclass specifically for showing issue modified date."""
  def __init__(self, issue, col, proxies_by_id, non_col_labels, label_values):
    self.type = artifactlist.CELL_TYPE_UNFILTERABLE
    self.value = framework.constants.NO_VALUES
    if issue.has_modified_timestamp():
      self.value = timestr.ComputeRelativeDate(
          issue.modified_timestamp(), recent_only=True)
      if not self.value:
        self.value = timestr.ComputeAbsoluteDate(issue.modified_timestamp())


# This maps column names to factories/constructors that make table cells.
_CELL_FACTORIES = {
    'id': TableCellID,
    'summary': TableCellSummary,
    'status': TableCellStatus,
    'owner': TableCellOwner,
    'stars': TableCellStars,
    'opened': TableCellOpened,
    'closed': TableCellClosed,
    'modified': TableCellModified,
    }
