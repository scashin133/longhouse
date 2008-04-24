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

"""Unit tests for issuelist module."""

from bo import dit_pb
from framework import artifactlist
from dit import issuelist
from dit import constants


class DisplayNameMock(object):

  def __init__(self, name):
    self.display_name = name


# TODO(students): make this work with pyunit.
class IssueListUnitTest(Object):

  def testMakeRowData(self):

    owner_id = 23456
    issue = _CreateIssue(
      owner_id=owner_id,
      labels=['Type-Defect', 'Priority-Medium'],
    )
    columns = _GetColumns()

    cell_factories = [
        issuelist._CELL_FACTORIES.get(col, artifactlist.TableCellKeyLabels)
        for col in columns]

    # a result is an artifactlist.TableRow object with a "cells" field
    # containing a list of artifactlist.TableCell objects.
    result = issuelist._MakeRowData(issue, columns, True,
      {owner_id: DisplayNameMock("Steve")}, cell_factories)

    self.assertEqual(len(columns), len(result.cells))

    for i in range(len(columns)):
      column = columns[i]
      cell = result.cells[i]
      self.assertEqual(i, cell.col_index)



def _CreateIssue(
      id=12345,
      owner_id=23456,
      labels=None,
      status=constants.DEFAULT_WELL_KNOWN_STATUSES[0], # presumably 'New'
      summary='Lame default summary.',
      summary_is_escaped=False,
      star_count=0,
      opened_timestamp=123456789,
      closed_timestamp=None,
      modified_timestamp=123456789):
  """Create a new issue with a bunch of dorky defaults."""

  issue = dit_pb.Issue()

  issue.set_id(id)
  issue.set_owner_id(owner_id)
  for label in labels:
    issue.add_labels(label)
  issue.set_status(status)
  issue.set_summary(summary)
  issue.set_summary_is_escaped(summary_is_escaped)
  issue.set_star_count(star_count)
  issue.set_opened_timestamp(opened_timestamp)
  issue.set_modified_timestamp(modified_timestamp)

  if closed_timestamp:
    issue.set_closed_timestamp(closed_timestamp)

  return issue


def _GetColumns():
  """Return a list of all well known column names."""

  columns = constants.DEFAULT_COL_SPEC.split()
  columns.extend(constants.OTHER_BUILT_IN_COLS)
  return [c.lower() for c in columns]


if __name__ == '__main__':
  # TODO: run the tests.
