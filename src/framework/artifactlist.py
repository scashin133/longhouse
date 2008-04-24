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

"""Helper functions for displaying lists of project artifacts.

This module exports the SortArtifacts function that does sorting of
business objects where each BO represents a project artifact (e.g., an
issue, download, or wiki page).  The sorting is done by extracting
relevant values from the PB using two dictionaries of accessor
functions: one or sortable fields, and another to get the logical
negative value of those fields for use when sorting in decending
order.

The desired sorting directives are specified in part of the user's
HTTP request.  This sort spec consists of the names of the columns
with optional minus signs to indicate descending sort order.

The tool configuration object also affects sorting.  When sorting by
fields defined by labels, the well-known labels are considered to come
before any non-well-known labels, and those well-known labels sort in
the order in which they are defined in the tool config PB.

This file also exports classes TableRow and TableCell that help
represent HTML table rows and cells.  These classes make rendering
HTML tables that list project artifacts much easier to do with EZT.

This file also exports ArtifactPagination that helps implement the
ability for the user to step through pages of artifact in a long list.
"""

from ezt import ezt

from twisted.python import log

from common import ezt_google
from framework import helpers
from framework import constants

from bo import artifact_pb


# A string that sorts after every other string.
_MAX_STRING = '~~~'

# We shorten long attribute values to fit into the table cells.
_MAX_CELL_DISPLAY_CHARS = 70


def SortArtifacts(req_info, artifacts, config,
                   asc_accessors, desc_accessors,
                   tie_breaker='id'):
  """Return a list of artifacts sorted by the user's sort specification.

  Args:
    req_info: commonly used info parsed from the request, including query.
    artifacts: an unsorted list of project artifact PBs.
    config: Project config PB instance that defines the sort order for
       labels and statuses in this project.
    asc_accessors: dictionary of (column_name -> accessor) to get values
       from the artifacts.
    desc_accessors: dictionary of (column_name -> accessor) to get logical
       negaive value of fields from the artifacts.
    tie_breaker: column name to add to the end of the sort spec if it is
       not already somewhere in the sort spec.

  Returns: a sorted list of issue ids that satisfy the query.

  The approach to sorting is an extension of the decorate-sort-undecorate
  pattern.  The extensions are that (a) we build lists with a variable number
  of fields to sort on, and (b) we allow individual fields to be sorted in
  descending order.  Even with the time taken to build the sort keys, calling
  sort() with no arguments seems to be faster overall than doing multiple
  stable-sorts or doing one sort using a multi-field comparison function.
  """
  # Prepend the end-user's sort spec to any project default sort spec.
  sort_spec = '%s %s' % (req_info.sort_spec, config.default_sort_spec())
  sort_directives = sort_spec.lower().split()

  # Build a list of accessors that will extract sort keys from the issues.
  accessors = [_MakeSortKeyAccessor(sd, config, asc_accessors, desc_accessors)
               for sd in sort_directives]
  if tie_breaker not in sort_directives:
    if tie_breaker.startswith('-'):
      accessors.append(desc_accessors[tie_breaker[1:]])
    else:
      accessors.append(asc_accessors[tie_breaker])
  accessors.append(lambda x: x)  # The artifact itself goes along for the ride.

  decorated_list = [[accessor(artifact) for accessor in accessors]
                    for artifact in artifacts]
  decorated_list.sort()
  result = [decorated_artifact[-1] for decorated_artifact in decorated_list]
  return result


def GetColSpec(req_info, config, site_wide_default):
  """Return column spec in request, or a default in the config or constant."""
  default_col_spec = config.default_col_spec() or site_wide_default
  col_spec = req_info.GetParam(
    'colspec', default_value=default_col_spec,
    antitamper_re=constants.COLSPEC_RE)
  return col_spec


def BuildListPrefs(config, site_wide_col_spec):
  """Return a dictionary of the data needed to populate the list prefs form."""
  ezt_data = {
    'default_col_spec': config.default_col_spec() or site_wide_col_spec,
    'default_sort_spec': config.default_sort_spec(),
    }
  if hasattr(config, 'default_x_attr'):
    ezt_data['default_x_attr'] = config.default_x_attr()
  if hasattr(config, 'default_y_attr'):
    ezt_data['default_y_attr'] = config.default_y_attr()
  return ezt_data


def ParseListPreferences(post_data, site_wide_col_spec):
  """Parse the part of a project admin form about artifact list preferences."""
  default_col_spec = ''
  if 'default_col_spec' in post_data:
    default_col_spec = post_data['default_col_spec'][0]
  if default_col_spec == site_wide_col_spec:
    default_col_spec = ''  # User is not trying to customize it.
  col_spec_words = constants.IDENTIFIER_RE.findall(default_col_spec)
  col_spec = ' '.join(col_spec_words)

  default_sort_spec = ''
  if 'default_sort_spec' in post_data:
    default_sort_spec = post_data['default_sort_spec'][0]
  log.msg('default_sort_spec = %s' % default_sort_spec)
  sort_spec_words = constants.IDENTIFIER_RE.findall(default_sort_spec)
  sort_spec = ' '.join(sort_spec_words)

  x_attr_str = ''
  if 'default_x_attr' in post_data:
    x_attr_str = post_data['default_x_attr'][0]
  x_attr_words = constants.IDENTIFIER_RE.findall(x_attr_str)
  x_attr = ''
  if x_attr_words:
    x_attr = x_attr_words[0]

  y_attr_str = ''
  if 'default_y_attr' in post_data:
    y_attr_str = post_data['default_y_attr'][0]
  y_attr_words = constants.IDENTIFIER_RE.findall(y_attr_str)
  y_attr = ''
  if y_attr_words:
    y_attr = y_attr_words[0]
  log.msg('default grid attrs = %s x %s' % (x_attr, y_attr))

  list_prefs = col_spec, sort_spec, x_attr, y_attr
  return list_prefs


def SetListPreferences(list_prefs, config):
  """Store the list preferences in a project tool config PB."""
  default_col_spec, default_sort_spec, x_attr, y_attr = list_prefs
  config.set_default_col_spec(default_col_spec)
  config.set_default_sort_spec(default_sort_spec)
  if hasattr(config, 'set_default_x_attr'):
    config.set_default_x_attr(x_attr)
  if hasattr(config, 'set_default_y_attr'):
    config.set_default_y_attr(y_attr)


def _MakeSortKeyAccessor(sort_directive, config,
                         asc_accessors, desc_accessors):
  """Return an accessor that extracts a sort key from a field of an issue.

  Args:
    sort_directive: string with column name and optional leading minus sign.
    config: ProjectIssueConfig instance that defines the sort order for
       labels and statuses in this project.
    asc_accessors: dictionary of (column_name -> accessor) to get values
       from the artifacts.
    desc_accessors: dictionary of (column_name -> accessor) to get logical
       negaive value of fields from the artifacts.

  Returns: an accessor function that can be applied to an issue to extract
  the relevant sort key value.
  """

  if sort_directive.startswith('-'):
    col_name = sort_directive[1:]
    descending = True
  else:
    col_name = sort_directive
    descending = False

  if col_name == 'status':  # 1. special case for issue status
    wk_statuses = [wks.status().lower()
                   for wks in config.well_known_statuses_list()]
    accessor = _IndexOrLexical(wk_statuses, asc_accessors[col_name],
                               descending)

  elif col_name in asc_accessors:  # 2. defined accessor functions
    if descending:
      accessor = desc_accessors[col_name]
    else:
      accessor = asc_accessors[col_name]

  # TODO: 3. handle sorting by users by names rather than user ids .

  else:  # 4. anything else is assumed to be a label prefix
    wk_labels = [wkl.label().lower()
                 for wkl in config.well_known_labels_list()]
    accessor = _IndexOrLexicalList(wk_labels, _MakeColumnAccessor(col_name),
                                   descending)

  return accessor


def _MakeColumnAccessor(col_name):
  """Make an accessor for an issue's labels that have col_name as a prefix.

  Args:
    col_name: string column name.

  Returns: an accessor that can be applied to an artifact to return a list of
    labels that have col_name as a prefix.

  For example, _MakeColumnAccessor('priority')(issue) could result in
  [], or ['priority-high'], or a longer list for multi-valued labels.
  """

  prefix = col_name + '-'

  def accessor(artifact):
    return [label.lower() for label in artifact.labels_list()
            if label.lower().startswith(prefix)]

  return accessor


def _IndexOrLexical(well_known_list, base_accessor, descending):
  """Return an accessor to score an artifact based on a user-defined ordering.

  Args:
    well_known_list: a ordered list of well-known values specified in the
      project tool configuration PB.  E.g., Priority-Medium comes before
      Priority-Low, even though that is not the lexigraphic order.
    base_accessor: function that gets a field from a given issue.
    descending: True if this accessor should give values that sort in the
      reverse of the normal order.

  Returns: an accessor that can be applied to an issue to return a suitable
  sort key.

  For example, when used to sort issue statuses, these accessors return an
  integer for well-known statuses, a string for odd-ball statuses, and an
  extreme value key for issues with no status.  That causes issues to appear
  in the expected order with odd-ball issues sorted lexigraphically after
  the ones with well-known status values, and issues with no defined status at
  the very end.  With descending set, the returned values cause the sort order
  to be reversed.
  """

  def accessor(artifact):
    value = base_accessor(artifact).lower()
    if not value:
      return _MAX_STRING  # Undefined values sort last.
    try:
      return well_known_list.index(value) # well-known by index
    except ValueError:
      return value  # odd-ball values after well-known and lexigraphically

  def negative_accessor(artifact):
    value = base_accessor(artifact).lower()
    if not value:
      return DescendingStr(_MAX_STRING)  # Undefined values sort first.
    try:
      return -well_known_list.index(value) # reverse of well-known index
    except ValueError:
      return DescendingStr(value) # These strings sort backwards.

  if descending:
    return negative_accessor
  else:
    return accessor


def _IndexOrLexicalList(well_known_list, list_accessor, descending):
  """Return an accessor to score an artifact based on a user-defined ordering.

  Args:
    well_known_list: a ordered list of well-known values specified in the
      project issue tracking configuration.
    list_accessor: function that gets a multi-valued field from a given issue.
    descending: True if this accessor should give values that sort in the
      reverse of the normal order.

  Returns: an accessor that can be applied to an issue to return a suitable
  sort key.

  When an artifact has multiple values for a given field (e.g., a defect
  occurs on multiple operating systems), we use the just the most favorable
  sorting key.
  """

  # TODO: consider whether it is worth it to generate all sort
  # keys for multi-valued fields rather than just the single most favorable.

  def accessor(artifact):
    value_list = list_accessor(artifact)

    if not value_list:
      return _MAX_STRING  # issues with no value sort to the end of the list.

    best_idx = None
    best_lex = None
    for value in value_list:
      try:
        idx = well_known_list.index(value)
        if best_idx is None or idx < best_idx:
          best_idx = idx
      except ValueError:
        if best_lex is None or value < best_lex:
          best_lex = value
    if best_idx is not None:
      return  best_idx #  If any value was well-known, rank it numerically
    return best_lex  # nothing was well known, rank this issue lexigraphically

  def negative_accessor(artifact):
    value_list = list_accessor(artifact)

    if not value_list:
      return DescendingStr(_MAX_STRING)  # issues with no value sort first.

    best_idx = None
    best_lex = None
    for value in value_list:
      try:
        idx = well_known_list.index(value)
        if best_idx is None or idx < best_idx:
          best_idx = idx
      except ValueError:
        if best_lex is None or value < best_lex:
          best_lex = value
    if best_idx is not None:
      return  -best_idx  # Reversed numerical ranking
    return DescendingStr(best_lex) # Reversed lexigraphically ranking

  if descending:
    return negative_accessor
  else:
    return accessor

class DescendingStr(object):
  """A string wrapper which reverses the sort order of strings.

  When compared to another DescendingStr, the sort order is reversed. Also,
  when compared to any other ptyhon object, the sort order is reversed.
  """

  def __init__(self, s):
    """Make a new object to wrap the given string."""
    self.s = s

  def __cmp__(self, other):
    """Return -1, 0, or 1 base on the reverse of the normal sort order."""
    if isinstance(other, DescendingStr):
      return cmp(other.s, self.s)
    else:
      return cmp(other, self.s)


def ComputeUnshownColumns(results, shown_columns, default_cols, built_in_cols):
  """Return a list of unshown columns that the user could add.

  Args:
    results: list of search result PBs. Each must have labels_list().
    shown_columns: list of column names to be used in results table.
    default_cols: list of column names that are shown by default.
      It is likely that the user would want to show one of these
      if it is not shown already.
    built_in_cols: list of other column names that built into the tool.
      E.g., star count, or creation date.

  Returns: list of column names to append to "..." menu.
  """
  unshown_list = []
  shown_dict = {}
  for col in shown_columns:
    shown_dict[col] = True

  # The user can always add any of the default columns.
  for col in default_cols:
    if col not in shown_dict and col not in unshown_list:
      unshown_list.append(col)

  # The user can always add any of the built-in columns.
  for col in built_in_cols:
    if col not in shown_dict and col not in unshown_list:
      unshown_list.append(col)

  # The user can add any column for any key-value label in the results.
  for r in results:
    for label_name in r.labels_list():
      if '-' in label_name:
        col, value = label_name.split('-', 1)
        col = col.capitalize()
        if col not in shown_dict and col not in unshown_list:
          unshown_list.append(col)

  return unshown_list


def ExtractUniqueValues(columns, artifact_list, proxies_by_id):
    """Build a nested list of unique values so the user can auto-filter.

    Args:
      columns: a list of lowercase column name strings.
      artifact_list: a list of artifacts in the complete set of search results.
      proxies_by_id: dict mapping gaia_ids to UserIDProxies.

    Returns: [EZTItem(col1, colname1, [val11, val12,...]), ...]
             A list of EZTItems, each of which has a col_index, column_name,
             and a list of unique values that appear in that column.
    """

    column_values = {}
    for col in columns:
      column_values[col] = {}

    unique_labels = {}
    for artifact in artifact_list:
      for label in artifact.labels_list():
        unique_labels[label] = True

    for label in unique_labels:
      if '-' in label:
        col, val = label.split('-', 1)
        col = col.lower()
        val_lower = val.lower()
        if col in column_values:
          if val_lower not in column_values[col]:
            column_values[col][val_lower] = val
      else:
        if 'summary' in column_values:
          label_lower = label.lower()
          if label_lower not in column_values['summary']:
            column_values['summary'][label_lower] = label

    if 'owner' in column_values:
      for artifact in artifact_list:
        if artifact.owner_id():
          owner_username = proxies_by_id[artifact.owner_id()].display_name
          if owner_username not in column_values['owner']:
            column_values['owner'][owner_username] = owner_username

    if 'stars' in column_values:
      for artifact in artifact_list:
        star_count = artifact.star_count()
        if star_count not in column_values['stars']:
          column_values['stars'][star_count] = star_count

    # TODO: handle reporters and cc usernames.

    if 'status' in column_values:
      for artifact in artifact_list:
        status = artifact.status()
        status_lower = status.lower()
        if status_lower not in column_values['status']:
          column_values['status'][status_lower] = status

    # TODO: sort each set of column values top-to-bottom, by the
    # order specified in the project artifact config.

    # Sort the column_value entries by the left-to-right column display order.
    result = []
    items = column_values.items()
    items.sort(lambda a,b: cmp(columns.index(a[0]), columns.index(b[0])))
    for i in range(len(items)):
      result.append(ezt_google.EZTItem(col_index=i,
                                       column_name=items[i][0],
                                       filter_values=items[i][1].values()))

    return result


class TableRow(object):
  """A tiny auxiliary class to represent a row in an HTML table."""

  def __init__(self, cells, owner_is_me):
    """Initialize the table row with the given data."""
    self.cells = cells
    self.owner_is_me = ezt.boolean(owner_is_me)  # Shows tiny ">" on my issues.

  def DebugString(self):
    """Return a string that is useful for on-page debugging."""
    return 'TR(%s)' % self.cells


CELL_TYPE_ID = 'ID'
CELL_TYPE_SUMMARY = 'summary'
CELL_TYPE_ATTR = 'attr'
CELL_TYPE_UNFILTERABLE = 'unfilterable'

class TableCell(object):
  """Helper class to represent a table cell when rendering using EZT."""

  def __init__(self, cell_type, values, non_column_labels=None):
    """Store all the given data for later access by EZT."""
    self.type = cell_type
    self.col_index = 0  # Is set afterward
    self.values = values
    value = ''
    if values is not None:
      self.value = ', '.join([str(v) for v in values])
    self.non_column_labels = non_column_labels

  def DebugString(self):
    return 'TC(%s, %s, %s, %s, %s)' % (self.type, self.column_name, self.value,
                                       self.cell_id, self.non_column_labels)


class TableCellKeyLabels(TableCell):
  """TableCell subclass specifically for showing user-defined label values."""
  def __init__(self, artifact, col, proxies_by_id,
               non_col_labels, label_values):
    self.type = CELL_TYPE_ATTR
    values = label_values.get(col, [constants.NO_VALUES])
    self.value = ', '.join(v for v in values)


def MakeGridData(artifacts, x_attr, x_headings, y_attr, y_headings,
                 proxies_by_id, artifact_proxy_factory, all_label_values):
  """Return a list of grid row items for display by EZT.

  Each grid row has a row name, and a list of cells.  Each cell has a
  list of tiles.  Each tile represents one artifact.  Artifacts are
  represented once in each cell that they match, so one artifact that
  has multiple values for a certain attribute can occur in multiple cells.
  """
  x_attr = x_attr.lower()
  y_attr = y_attr.lower()

  grid_data = []
  for y in y_headings:
    cells_in_row = []
    for x in x_headings:
      tiles = []
      for art in artifacts:
        belongs = BelongsInCell(art, x_attr, x, y_attr, y,
                                proxies_by_id, all_label_values[art.id()])
        if belongs:
          tiles.append(artifact_proxy_factory(art))
      # TODO: implement a Tile class.  For now, just
      # use the proxy for the underlying artifact.
      drill_down = '%s:%s %s:%s' % (x_attr, x, y_attr, y)
      if x == constants.NO_VALUES or y == constants.NO_VALUES:
        drill_down = ''  # We have no way to search for "----"
      cells_in_row.append(ezt_google.EZTItem(
        tiles=tiles, count=len(tiles), drill_down=drill_down))
    grid_data.append(ezt_google.EZTItem(grid_y_heading=y,
                                        cells_in_row=cells_in_row))
  return grid_data


def MakeLabelValuesDict(art):
  """Return a dict of label values and a list of one-word labels.

  Args:
    art: artifact object, e.g., an issue PB.

  Returns: (label_values, one_word_labels), where label_values is
    a dict {prefix: [suffix,...], ...} for each Key-Valye label, and
    one_word_labels is a list of all the artifact labels that do not
    have a hyphen.
  """
  label_values = {}
  one_word_labels = []

  for label_name in art.labels_list():
    if '-' not in label_name:
      one_word_labels.append(label_name)
    else:
      key, value = label_name.split('-', 1)
      key = key.lower()
      if key not in label_values:
        label_values[key] = []
      label_values[key].append(value)

  return label_values, one_word_labels


def BelongsInCell(art, x_attr, x_val, y_attr, y_val,
                  proxies_by_id, label_value_dict):
  """Return true if an artifact should be shown inside a grid cell.

  Args:
    art: artifact object, e.g., an issue PB.
    x_attr: artifact attribute that determines the x coordinate, or None.
    x_val: the x coordinate of the cell being concidered.
    y_attr: artifact attribute that determines the y coordinate, or None.
    y_val: the y coordinate of the cell being concidered.
    proxies_by_id: dictionary of UserIDProxies already created.
    label_value_dict: dictionary of artifact label values already computed.
  """
  fits_x, fits_y = True, True
  if x_attr:
    vals = GetArtifactAttr(art, x_attr, proxies_by_id, label_value_dict)
    fits_x = x_val in vals

  if y_attr:
    vals = GetArtifactAttr(art, y_attr, proxies_by_id, label_value_dict)
    fits_y = y_val in vals

  return fits_x and fits_y


def GetArtifactAttr(art, attribute_name, proxies_by_id,
                    label_attr_values_dict):
  """Return the requested attribute values of the given artifact."""
  if attribute_name == 'id':
    return [art.id()]
  if attribute_name == 'summary':
    return [art.summary()]
  if attribute_name == 'status':
    return [art.status()]
  if attribute_name == 'stars':
    return [art.star_count()]
  if attribute_name == 'owner':
    if not art.has_owner_id():
      return [constants.NO_VALUES]
    else:
      return [proxies_by_id[art.owner_id()].display_name]

  # Since it is not a built-in attribute, it must be a Key-Value label
  return label_attr_values_dict.get(attribute_name, [constants.NO_VALUES])


def AnyArtifactHasNoAttr(artifacts, attr_name,
                         proxies_by_id, all_label_values):
  """Return true if any artifact does not have a value for attr_name."""
  for art in artifacts:
    vals = GetArtifactAttr(art, attr_name.lower(), proxies_by_id,
                           all_label_values[art.id()])
    if constants.NO_VALUES in vals:
      return True
  return False


class VirtualPagination(object):
  """An object to calculate Prev and Next pagination links."""
  def __init__(self, req_info, total_count, items_per_page, list_page_url,
               count_up=True):
    """Given 'num' and 'start' params, determine Prev and Next links.

    Args:
      req_info: commonly used info parsed from the request.
      total_count: total number of artifacts that satisfy the query.
      items_per_page: number of items to display on each page, e.g., 25.
      list_page_url: URL of the web application page that is displaying
        the list of artifacts.  Used to build the Prev and Next URLs.
      count_up: if False, count down from total_count.
    """
    self.total_count = total_count
    self.prev_url = ''
    self.next_url = ''

    self.num = req_info.GetIntParam('num', items_per_page)
    if count_up:
      self.start = req_info.GetIntParam('start', 0)
      self.last = min(self.total_count, self.start + self.num)
      prev_start = max(0, self.start - self.num)
      next_start = self.start + self.num
    else:
      self.start = req_info.GetIntParam('start', self.total_count)
      self.last = max(0, self.start - self.num)
      prev_start = min(self.total_count, self.start + self.num)
      next_start = self.start - self.num

    list_servlet_rel_url = list_page_url.split('/')[-1]
    if prev_start != self.start:
      self.prev_url = helpers.FormatURL(
        req_info, list_servlet_rel_url, start=prev_start)
    if ((count_up and next_start < self.total_count) or
        (not count_up and next_start >= 1)):
      self.next_url = helpers.FormatURL(
        req_info, list_servlet_rel_url, start=next_start)

    self.visible = ezt.boolean(self.last != self.start)

    # Adjust indices to one-based values for display to users.
    if count_up:
      self.start = self.start + 1
    else:
      self.last = self.last + 1

  def DebugString(self):
    """Return a string that is useful in on-page debugging."""
    return '%s - %s of %s; prev_url:%s; next_url:%s' % (
      self.start, self.last, self.total_count, self.prev_url, self.next_url)


class ArtifactPagination(VirtualPagination):
  """An object to calculate Prev and Next pagination links."""

  def __init__(self, req_info, results, items_per_page, list_page_url):
    """Given 'num' and 'start' params, determine Prev and Next links.

    Args:
      req_info: commonly used info parsed from the request.
      results: a list of artifact ids that satisfy the query.
      items_per_page: number of items to display on each page, e.g., 25.
      list_page_url: URL of the web application page that is displaying
        the list of artifacts.  Used to build the Prev and Next URLs.
    """
    VirtualPagination.__init__(
      self, req_info, len(results), items_per_page, list_page_url)
    self.visible_results = results[self.start - 1 : self.start - 1 + self.num]
