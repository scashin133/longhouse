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

"""Unit tests for ArtifactList helper functions.
"""

from framework import artifactlist


class MockArtifact(object):
  def __init__(self, labels):
    self.labels = labels

  def labels_list(self):
    return self.labels

EMPTY_SEARCH_RESULTS = []

SEARCH_RESULTS_WITH_LABELS = [
  MockArtifact('Priority-High Milestone-1.0'.split()),
  MockArtifact('Priority-High Milestone-1.0'.split()),
  MockArtifact('Priority-Low Milestone-1.1'.split()),
  # 'Visibility-Super-High' tests that only first dash counts
  MockArtifact('Visibility-Super-High'.split()),
  ]


# TODO(students): make this work with pyunit.
class ArtifactListUnitTest(Object):

  def setUp(self):
    self.default_cols = 'a b c'
    self.builtin_cols = 'a b x y z'

  def testComputeUnshownColumns_CommonCase(self):
    shown_cols = 'a b c'

    unshown = artifactlist.ComputeUnshownColumns(
      EMPTY_SEARCH_RESULTS, shown_cols.split(),
      self.default_cols.split(), self.builtin_cols.split())
    self.assertEquals(unshown, 'x y z'.split())

    unshown = artifactlist.ComputeUnshownColumns(
      SEARCH_RESULTS_WITH_LABELS, shown_cols.split(),
      self.default_cols.split(), self.builtin_cols.split())
    self.assertEquals(unshown, 'x y z Priority Milestone Visibility'.split())

  def testComputeUnshownColumns_MoreBuiltins(self):
    shown_cols = 'a b c x y'

    unshown = artifactlist.ComputeUnshownColumns(
      EMPTY_SEARCH_RESULTS, shown_cols.split(),
      self.default_cols.split(), self.builtin_cols.split())
    self.assertEquals(unshown, 'z'.split())

    unshown = artifactlist.ComputeUnshownColumns(
      SEARCH_RESULTS_WITH_LABELS, shown_cols.split(),
      self.default_cols.split(), self.builtin_cols.split())
    self.assertEquals(unshown, 'z Priority Milestone Visibility'.split())

  def testComputeUnshownColumns_NotAllDefaults(self):
    shown_cols = 'a b'

    unshown = artifactlist.ComputeUnshownColumns(
      EMPTY_SEARCH_RESULTS, shown_cols.split(),
      self.default_cols.split(), self.builtin_cols.split())
    self.assertEquals(unshown, 'c x y z'.split())

    unshown = artifactlist.ComputeUnshownColumns(
      SEARCH_RESULTS_WITH_LABELS, shown_cols.split(),
      self.default_cols.split(), self.builtin_cols.split())
    self.assertEquals(unshown, 'c x y z Priority Milestone Visibility'.split())

  def testComputeUnshownColumns_ExtraNonDefaults(self):
    shown_cols = 'a b c d e f'

    unshown = artifactlist.ComputeUnshownColumns(
      EMPTY_SEARCH_RESULTS, shown_cols.split(),
      self.default_cols.split(), self.builtin_cols.split())
    self.assertEquals(unshown, 'x y z'.split())

    unshown = artifactlist.ComputeUnshownColumns(
      SEARCH_RESULTS_WITH_LABELS, shown_cols.split(),
      self.default_cols.split(), self.builtin_cols.split())
    self.assertEquals(unshown, 'x y z Priority Milestone Visibility'.split())

  def testComputeUnshownColumns_ExtraNonDefaults(self):
    shown_cols = 'a b c d e f'

    unshown = artifactlist.ComputeUnshownColumns(
      EMPTY_SEARCH_RESULTS, shown_cols.split(),
      self.default_cols.split(), self.builtin_cols.split())
    self.assertEquals(unshown, 'x y z'.split())

    unshown = artifactlist.ComputeUnshownColumns(
      SEARCH_RESULTS_WITH_LABELS, shown_cols.split(),
      self.default_cols.split(), self.builtin_cols.split())
    self.assertEquals(unshown, 'x y z Priority Milestone Visibility'.split())

  def testComputeUnshownColumns_UserColumnsShown(self):
    shown_cols = 'a b c Priority'

    unshown = artifactlist.ComputeUnshownColumns(
      EMPTY_SEARCH_RESULTS, shown_cols.split(),
      self.default_cols.split(), self.builtin_cols.split())
    self.assertEquals(unshown, 'x y z'.split())

    unshown = artifactlist.ComputeUnshownColumns(
      SEARCH_RESULTS_WITH_LABELS, shown_cols.split(),
      self.default_cols.split(), self.builtin_cols.split())
    self.assertEquals(unshown, 'x y z Milestone Visibility'.split())

  def testComputeUnshownColumns_EverythingShown(self):
    shown_cols = 'a b c x y z Priority Milestone Visibility'

    unshown = artifactlist.ComputeUnshownColumns(
      EMPTY_SEARCH_RESULTS, shown_cols.split(),
      self.default_cols.split(), self.builtin_cols.split())
    self.assertEquals(unshown, ''.split())

    unshown = artifactlist.ComputeUnshownColumns(
      SEARCH_RESULTS_WITH_LABELS, shown_cols.split(),
      self.default_cols.split(), self.builtin_cols.split())
    self.assertEquals(unshown, ''.split())

  def testComputeUnshownColumns_NothingShown(self):
    shown_cols = ''

    unshown = artifactlist.ComputeUnshownColumns(
      EMPTY_SEARCH_RESULTS, shown_cols.split(),
      self.default_cols.split(), self.builtin_cols.split())
    self.assertEquals(unshown, 'a b c x y z'.split())

    unshown = artifactlist.ComputeUnshownColumns(
      SEARCH_RESULTS_WITH_LABELS, shown_cols.split(),
      self.default_cols.split(), self.builtin_cols.split())
    self.assertEquals(unshown,
                      'a b c x y z Priority Milestone Visibility'.split())

  def testComputeUnshownColumns_NoBuiltins(self):
    shown_cols = 'a b c'
    default_cols = 'a b c'
    builtin_cols = ''

    unshown = artifactlist.ComputeUnshownColumns(
      EMPTY_SEARCH_RESULTS, shown_cols.split(),
      default_cols.split(), builtin_cols.split())
    self.assertEquals(unshown, ''.split())

    unshown = artifactlist.ComputeUnshownColumns(
      SEARCH_RESULTS_WITH_LABELS, shown_cols.split(),
      default_cols.split(), builtin_cols.split())
    self.assertEquals(unshown, 'Priority Milestone Visibility'.split())

if __name__ == '__main__':
  # TODO: run the tests
