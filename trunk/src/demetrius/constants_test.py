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

"""Unittest for constants module"""

from demetrius import constants

# TODO(students): make this work with pyunit.
class ProjectNameRegexpTest(Object):
  """Test the project name validator regular expression."""

  def setUp(self):
    """Pre-test setup.

    Saves some constants to instance variables for readability.
    """
    self.matcher = constants.RE_PROJECT_NAME.match
    self.max_len = constants.MAX_PROJECT_NAME_LENGTH
    self.min_len = constants.MIN_PROJECT_NAME_LENGTH

  def testInvalidProjectNames(self):
    """Test known illegal name examples.

    The matcher should return a false value for all of the examples.
    """
    cases = (
      ('19204', 'Project names cannot be all digits.'),
      ('19-04', 'Project names need at least one letter.'),
      ('-project', 'Project names cannot start with a "-"'),
      ('c'*(self.max_len+1), 'Project names cannot be more than %d characters '
                             'long.' % self.max_len),
      ('fo', 'Project names must be at least %d characters '
             'long' % self.min_len)
    )
    for name, explanation in cases:
      self.failIf(self.matcher(name), explanation)

  def testValidProjectNames(self):
    """Test known legal name examples.

    The matcher should return a true value for all of the examples.
    """
    cases = (
      ('19abc', 'Project names with digits and letters okay.'),
      ('19-04a', 'Project names with all digits + 1 letter okay.'),
      ('proj-', 'Project names ending with "-" are okay.'),
      ('c'*self.max_len, 'Project names can be up to %d characters '
                         'long.' % self.max_len),
      ('foo', 'Project names can be %d or more characters '
              'long.' % self.min_len)
    )
    for name, explanation in cases:
      self.failUnless(self.matcher(name), explanation)

if __name__ == '__main__':
  # TODO: run the tests.
