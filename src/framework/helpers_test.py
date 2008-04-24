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

"""Unit tests for Demetrius RequestInfo class.
"""


# TODO(students): make this work with pyunit.

from google3.codesite.framework import helpers

class HelpersUnitTest(Object):

  def testConvertUserNameToEmail(self):
    self.assertEquals(helpers.ConvertEditNameToEmail('user1'),
                      'user1@gmail.com')
    self.assertEquals(helpers.ConvertEditNameToEmail('user2@domain.com'),
                      'user2@domain.com')
    self.assertEquals(helpers.ConvertEditNameToEmail('user3@do.main.com'),
                      'user3@do.main.com')


if __name__ == '__main__':
  # TODO: run the tests
