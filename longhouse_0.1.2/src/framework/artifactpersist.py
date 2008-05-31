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

"""A set of helper functions for persistence for Demetrius artifacts.

This module provides functions to get, update, create, and (in some
cases) delete Artifact and ArtifactComment business objects.

The Artifact and ArtifactComment business objects are low-level records that
can be reused in the description of more complicated business objects.  They
are described in bo/artifact.py.

Unlike other persist files, this file does not define a class, or open
its own file.  And, this class is not intended to be used
directly from servlet classes.  Instead, this code is called from
component-specific persist classes and the appropriate file is passed
in.
"""

import sys

from twisted.python import log

from bo import artifact_pb
from framework import persist

ARTIFACT_COMMENT_COLUMN = 'Comment:'

def GetAllArtifactComments(table, key, column=ARTIFACT_COMMENT_COLUMN,
                           bo_class=artifact_pb.ArtifactComment):
  """Return a list of ArtifactComments for the artifact at that row key."""
  comments = []
  # TODO(students): retrieve all user comments on an artifact.
  return comments


def AddArtifactComment(transaction, comment, column=ARTIFACT_COMMENT_COLUMN):
  """Store a comment via a transaction that may also update an artifact."""
  log.msg('Preparing to store artifact comment')
  transaction.Set(column, comment.Encode())


def UpdateComment(transaction, comment, column=ARTIFACT_COMMENT_COLUMN):
  """Store the comment at the given timestamp."""
  transaction.SetAtTimestamp(column, comment.microtimestamp, comment.Encode())


def UpdateConfigCommentSettings(comment_settings, config):
  """Update the tool config with the given comment settings."""
  allow_comments, comment_notify_address = comment_settings
  config.set_allow_comments(allow_comments)
  config.set_comment_notify_address(comment_notify_address)

if __name__ == '__main__':
  sys.exit('This is not meant to be run as a standalone program. Exiting.')
