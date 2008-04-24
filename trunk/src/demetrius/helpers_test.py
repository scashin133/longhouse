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

"""Unit tests for helpers module."""

from bo import demetrius_pb
from demetrius import helpers

# TODO(students): make this work with pyunit
class HelpersUnitTest(Object):

  def testBuildProjectLinks(self):

    project = demetrius_pb.Project()

    project.set_state(demetrius_pb.Project.HIDDEN)

    results = helpers.BuildProjectLinks(
      project,
      groups=[
        ('Foo Group', 'Foo'),
        ('Sna Chat', 'SnaChatz')],
      urls=[
        ('Apache', 'http://apache.org'),
        ('Google', 'http://www.google.com/')],
      blogs=[
        ('Snappy Blog', 'http://snappy.com/myblog')],
    )

    self.assert_(results.has_key('url_links'))
    self.assert_(results.has_key('group_links'))
    self.assert_(results.has_key('blog_links'))

    links = results['group_links']
    self.assertEqual(2, len(links))

    link = links[0]
    self.assertEqual('Foo Group', link.label)
    self.assertEqual('Foo', link.group_name)

    link = links[1]
    self.assertEqual('Sna Chat', link.label)
    self.assertEqual('SnaChatz', link.group_name)

    links = results['url_links']
    self.assertEqual(2, len(links))

    link = links[0]
    self.assertEqual('Apache', link.label)
    self.assertEqual('http://apache.org', link.direct_url)
    self.assert_(link.url) # will be defined, but may be a redirect

    link = links[1]
    self.assertEqual('Google', link.label)
    self.assertEqual('http://www.google.com/', link.direct_url)
    self.assert_(link.url) # will be defined, but may be a redirect

    links = results['blog_links']
    self.assertEqual(1, len(links))

    link = links[0]
    self.assertEqual('Snappy Blog', link.label)
    self.assertEqual('http://snappy.com/myblog', link.direct_url)
    self.assert_(link.url) # will be defined, but may be a redirect


if __name__ == '__main__':
  # TODO: run the tests
