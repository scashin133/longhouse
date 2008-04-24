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

"""Some constants used throughout the demetrius system.
"""

import re

# Do not change these, they will be set at runtime by run.py
WORKING_DIR = ""
SVN_LOC = ""

# persistence constants:

# location for storing local file
# e.g. user information, global longhouse information
LOCAL_STORAGE_ROOT = 'storage/'

# root of all persisted files
# (actual root is be WORKING_DIR/PERSIST_ROOT)
VERSIONED_STORAGE_ROOT = 'storage/working_copies/'

# storage location for projects which have not registered
# a subversion server for longhouse to write to
UNVERSIONED_STORAGE_ROOT = 'storage/unversioned/'

# local disk (large users file, large projects file)
LD_USERS = 'users.xml'
LD_PROJECTS = 'projects.xml'

# working copy (per-project information)
WC_PROJECT = '%projectname%/project.xml'
WC_ISSUES = '%projectname%/issues.xml'
WC_ISSUES_COMMENTS = '%projectname%/issuecomments.xml'
WC_ISSUES_USER_ISSUE_STARS = '%projectname%/issues-userissuestars.xml'
WC_ISSUES_ISSUE_USER_STARS = '%projectname%/issues-issueuserstars.xml'

# Number of seconds in one day.
SECS_PER_DAY = 60 * 60 * 24
SECS_PER_YEAR = SECS_PER_DAY * 365

# Size in bytes of the largest form submission that we will accept
MAX_POST_BODY_SIZE = 10 * 1024 * 1024   # = 10 MB

# Special user id and name to use when no user was specified.
NO_USER_SPECIFIED = 0
NO_USER_NAME = '---'

# String to display when some field has no value.
NO_VALUES = '----'

# TODO(jrobbins): move the actual sevlets for these pages under the
# framework directory too.  They are servlets that explain framework
# features to end-users.

# URLs of site-wide demetrius pages
EXCESSIVE_ACTIVITY_PAGE_URL = '/hosting/excessiveActivity'
NONPROJECT_COLLISION_PAGE_URL = '/hosting/collision'

# URLs of demetrius project pages
ARTIFACT_COLLISION_PAGE_URL = '/collision'


# Used to loosely validate column spec. Mainly guards against malicious input.
COLSPEC_RE = re.compile(r'^[\w\s]*$')

# Used to loosely validate sort spec. Mainly guards against malicious input.
SORTSPEC_RE = re.compile(r'^[-\w\s]*$')

# Regular expressions used in parsing label and status configuration text
IDENTIFIER_REGEX = r'[^ \t\n,=][^ \t\n,=]+'
IDENTIFIER_RE = re.compile(IDENTIFIER_REGEX, re.UNICODE)
IDENTIFIER_DOCSTRING_RE = re.compile(
  r'^(%s)[ \t]*=?[ \t]*(.*)$' % IDENTIFIER_REGEX,
  re.MULTILINE | re.UNICODE)

# Expiration time for special features of timestamped links.
# This is not for security, just for informational messages that
# make sense in the context of a user session, but that should
# not appear days later if the user follows a bookmarked link.
LINK_EXPIRATION_SEC = 8
