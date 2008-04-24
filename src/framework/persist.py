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

"""A set of utility functions for persistence for Demetrius.
"""


class Error(Exception):
  """Base exception class for this package."""


class MidAirCollision(Error):
  """The item was updated by another user at the same time."""

  def __init__(self, name, continue_url):
    """Store fields that are useful in handling the exception"""
    self.name = name  # human-readable name for the artifact being edited.
    self.continue_url = continue_url  # URL of page to start over.
