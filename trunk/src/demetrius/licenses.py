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

"""Define the allowable licenses for hosted projects.

We have taken the position that projects hosted at this site may only
choose from a limited set of licenses for their project. We support
the idea of reducing license proliferation, and our set of allowed
licenses is one way to do that.

Three variables are available:

  USER_LICENSES: a raw dictionary of allowable licenses that may
                 be attached to projects by users
  ADMIN_LICENSES: a dictionary of licenses that may only be attached
                  to a project by site admins
  ALL_LICENSES: a dictionary that is the union of USER_LICENSES and
                and ADMIN_LICENSES.
"""

# The set of allowed licenses.
USER_LICENSES = {
  'asf20': ('Apache License 2.0',
            'http://www.apache.org/licenses/LICENSE-2.0'),
  'art': ('Artistic License/GPLv2',
          'http://dev.perl.org/licenses/'),
  'lgpl': ('GNU Lesser General Public License',
           'http://www.gnu.org/licenses/lgpl.html'),
  'gpl2': ('GNU General Public License v2',
           'http://www.gnu.org/licenses/old-licenses/gpl-2.0.html'),
  'gpl3': ('GNU General Public License v3',
           'http://www.gnu.org/licenses/gpl.html'),
  'bsd': ('New BSD License',
          'http://www.opensource.org/licenses/bsd-license.php'),
  'mpl11': ('Mozilla Public License 1.1',
            'http://www.mozilla.org/MPL/'),
  'mit': ('MIT License',
          'http://www.opensource.org/licenses/mit-license.php'),
  }

ADMIN_LICENSES = {
  'multiple': ('Multiple Licenses',
               'http://code.google.com/multiple_licenses.html'),
  'gsoc': ('See source code',
               'http://code.google.com/see_source_code_license.html'),
  }

ALL_LICENSES = {}
ALL_LICENSES.update(USER_LICENSES)
ALL_LICENSES.update(ADMIN_LICENSES)
