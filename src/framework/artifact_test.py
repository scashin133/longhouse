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

"""Unit tests for Artifact helper functions.
"""

from common import ezt_google
from framework import artifact


ORIG_SUMMARY = 'this is the orginal summary'
ORIG_LABELS = ['one', 'two']

TEST_USER_ID = 101010101
TEST_CONTENT = 'this is the content of a comment'
TEST_SUMMARY = 'some comments update summary and others do not'
TEST_LABELS1 = ['some', 'comments', 'have', 'labels ', ' ', '']
TEST_LABELS2 = []


class MockRequestInfo(object):
  logged_in_user_id = TEST_USER_ID


class MockArtifact(object):
  def summary(self):
    return ORIG_SUMMARY

  def labels_list(self):
    return ORIG_LABELS


# TODO(Students): make this work with pyunit.
class ArtifactUnitTest(Object):

  def setUp(self):
    self.req_info = MockRequestInfo()
    self.art = MockArtifact()
    self.error = ezt_google.EZTError()

  def assertArtifactNeverChangesAndNoErrors(self):
    """The artifact is const, even though the comment notes updates to it."""
    self.assertEquals(self.art.summary(), ORIG_SUMMARY)
    self.assertEquals(self.art.labels_list(), ORIG_LABELS)
    self.assertFalse(self.error.AnyErrors())

  def testLoadCommentFromPostJustContent(self):
    post_dict = {
      'content': [TEST_CONTENT],
      }

    ac = artifact.LoadCommentFromPost(
      post_dict, self.req_info, self.art, self.error)

    self.assertEquals(ac.content(), TEST_CONTENT)
    self.assertEquals(ac.creator_user(), TEST_USER_ID)
    self.assertArtifactNeverChangesAndNoErrors()

  def testLoadCommentFromPostAddContentChangeSummary(self):
    post_dict = {
      'content': [TEST_CONTENT],
      'summary': [TEST_SUMMARY],
      'label': ORIG_LABELS,
      }

    ac = artifact.LoadCommentFromPost(
      post_dict, self.req_info, self.art, self.error)

    self.assertEquals(ac.content(), TEST_CONTENT)
    self.assertEquals(ac.creator_user(), TEST_USER_ID)
    self.assertEquals(len(ac.updates_list()), 1)
    self.assertArtifactNeverChangesAndNoErrors()

  def testLoadCommentFromPostAddContentChangeLabels(self):
    post_dict = {
      'content': [TEST_CONTENT],
      'summary': [ORIG_SUMMARY],
      'label': TEST_LABELS1,
      }

    ac = artifact.LoadCommentFromPost(
      post_dict, self.req_info, self.art, self.error)

    self.assertEquals(ac.content(), TEST_CONTENT)
    self.assertEquals(ac.creator_user(), TEST_USER_ID)
    self.assertEquals(len(ac.updates_list()), 1)
    self.assertArtifactNeverChangesAndNoErrors()

  def testLoadCommentFromPostAddContentRemoveAllLabels(self):
    post_dict = {
      'content': [TEST_CONTENT],
      'summary': [ORIG_SUMMARY],
      'label': TEST_LABELS2,
      }

    ac = artifact.LoadCommentFromPost(
      post_dict, self.req_info, self.art, self.error)

    self.assertEquals(ac.content(), TEST_CONTENT)
    self.assertEquals(ac.creator_user(), TEST_USER_ID)
    self.assertEquals(len(ac.updates_list()), 1)
    self.assertArtifactNeverChangesAndNoErrors()


if __name__ == '__main__':
  # TODO: run the tests
