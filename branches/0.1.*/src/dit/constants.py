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

"""Some constants used in the DIT pages.
"""

import re


# URLs of DIT project pages
ISSUE_LIST_PAGE_URL = '/issues/list'
ISSUE_DETAIL_PAGE_URL = '/issues/detail'
ISSUE_UPDATE_FORM_URL = '/issues/update.do'
ISSUE_COMMENT_DELETION_FORM_URL = '/issues/delComment.do'
ISSUE_SETSTAR_FORM_URL = '/issues/setstar.do'
ISSUE_ENTRY_PAGE_URL = '/issues/entry'
ISSUE_ENTRY_FORM_URL = '/issues/entry.do'
ISSUE_OPTIONS_FEED_URL = '/feeds/issueOptions'
ISSUE_ADVSEARCH_PAGE_URL = '/issues/advsearch'
ISSUE_ADVSEARCH_FORM_URL = '/issues/advsearch.do'
ISSUE_TIPS_PAGE_URL = '/issues/searchtips'
ISSUE_ATTACHMENT_PAGE_URL = '/issues/attachment'
ADMIN_ISSUES_PAGE_URL = '/adminIssues'
ADMIN_ISSUES_FORM_URL = '/adminIssues.do'

# Default columns shown on issue list page, and other built-in cols.
DEFAULT_COL_SPEC = 'ID Type Status Priority Milestone Owner Summary'
OTHER_BUILT_IN_COLS = ['Stars', 'Opened', 'Closed', 'Modified']

# Issues per page in the issue list
DEFAULT_RESULTS_PER_PAGE = 100

# Search field input indicating that the user wants to
# jump to the specified issue.
JUMP_RE = re.compile('^\d+$')

# Regular expression defining a single search term.
# Used when parsing the contents of the issue search field.
TERM_RE = re.compile('[-a-zA-Z0-9._]+')

# Regular expression to detect issue references.
# Used to auto-link to other issues when displaying issue details.
# Matches "issue " when "issue" is not part of a larger word, or
# "issue #", or just a "#" when it is preceeded by a space.
ISSUE_REF_RE = re.compile(r'(\bissue\s*#?)(\d+)\b',
                          re.IGNORECASE | re.MULTILINE)


# The next few items are specifications of the defaults for project
# issue configurations.  These are used for projects that do not have
# their own config.

DEFAULT_CANNED_QUERIES = [
  ('All Issues', ''),
  ('Open Issues', 'is:open'),
  ('Issues Assigned to Me', 'owner:me'),
  ('Issues Reported by Me', 'reporter:me'),
  ('My Starred Issues', 'is:starred'),
  ('New Issues', 'status:new'),
  ('Issues to Verify', 'isnot:open status!=verified'),
  ]

# Define well-known issue statuses.  Each status has 3 parts: a name, a
# description, and True if the status means that an issue should be
# considered to be open or False if it should be considered closed.
DEFAULT_WELL_KNOWN_STATUSES = [
  ('New', 'Issue has not had initial review yet', True),
  ('Accepted', 'Problem reproduced / Need acknowledged', True),
  ('Started', 'Work on this issue has begun', True),
  ('Fixed', 'Developer made requested changes, QA should verify', False),
  ('Verified', 'QA has verified that the fix worked', False),
  ('Invalid', 'This was not a valid issue report', False),
  ('Duplicate', 'This report duplicates an existing issue', False),
  ('WontFix', 'We decided to not take action on this issue', False),
  ]

DEFAULT_WELL_KNOWN_LABELS = [
  ('Type-Defect', 'Report of a software defect'),
  ('Type-Enhancement', 'Request for enhancement'),
  ('Type-Task', 'Work item that doesn\'t change the code or docs'),
  ('Type-Patch', 'Source code patch for review'),
  ('Type-Other', 'Some other kind of issue'),
  ('Priority-Critical', 'Must resolve in the specified milestone'),
  ('Priority-High', 'Strongly want to resolve in the specified milestone'),
  ('Priority-Medium', 'Normal priority'),
  ('Priority-Low', 'Might slip to later milestone'),
  ('OpSys-All', 'Affects all operating systems'),
  ('OpSys-Windows', 'Affects Windows users'),
  ('OpSys-Linux', 'Affects Linux users'),
  ('OpSys-OSX', 'Affects Mac OS X users'),
  ('Milestone-Release1.0', 'All essential functionality working'),
  ('Component-UI', 'Issue relates to program UI'),
  ('Component-Logic', 'Issue relates to application logic'),
  ('Component-Persistence', 'Issue relates to data storage components'),
  ('Component-Scripts', 'Utility and installation scripts'),
  ('Component-Docs', 'Issue relates to end-user documentation'),
  ('Security', 'Security risk to users'),
  ('Performance', 'Performance issue'),
  ('Usability', 'Affects program usability'),
  ('Maintainability', 'Hinders future changes'),
  ]

DEFAULT_EXCL_LABEL_PREFIXES = ['Type', 'Priority', 'Milestone']

DEFAULT_WELL_KNOWN_PROMPTS = [
  ('User defect report',
   'What steps will reproduce the problem?\\n1. \\n2. \\n3. \\n\\nWhat is the expected output? What do you see instead?\\n\\n\\n\\nWhat version of the product are you using? On what operating system?\\n\\n\\nPlease provide any additional information below.\\n'),
  ('Developer defect report',
   'What steps will reproduce the problem?\\n1. \\n2. \\n3. \\n\\nWhat is the expected output? What do you see instead?\\n\\n\\nPlease use labels and text to provide additional information.\\n'),
  ('User enhancement request',
   'What are the details of the enhancement to be added to the product?\\n\\n\\nWhat is the nature of this enhancement? (functionality, usability, security, etc)\\n\\n\\nHow will this enhancement help system users?\\n\\n\\nWhat version of the product are you using? On what operating system?\\n\\n\\n\\nPlease provide any additional information below.\\n'),
  ('Developer enhancement request',
   'What are the details of the enhancement to be added to the product?\\n\\n\\nWhat is the nature of this enhancement? (functionality, usability, security, etc)\\n\\n\\nHow will this enhancement help system users?\\n\\n\\nWhat is a suggested means of implementing this enhancement?\\n\\n\\nPlease use labels and text to provide additional information.\\n'),
  ('User task request',
   'What is the task you wish to be performed?\\n\\n\\nWhat benefit will be gained from performing this task?\\n\\n\\nPlease provide any additional information below.\\n'),
  ('Developer task request',
   'What is the task you wish to be performed?\\n\\n\\nWhat benefit will be gained from performing this task?\\n\\n\\nWhat is a suggested means of performing this task?\\n\\n\\nPlease use labels and text to provide additional information.\\n'),
  ('User patch review request',
   'What are the nature of the changes contained in the patch you want to submit for review?\\n\\n\\nWhy do you think these changes are necessary?\\n\\n\\nPlease attach the files associated with this patch to this issue. Alternatively, please specify where the files can be found:\\n\\n\\n'),
  ('User other issue report',
   'What is the issue you are reporting?\\n\\n\\nWhy are you reporting this issue?\\n\\n\\nWhat version of the product are you using? On what operating system?\\n\\n\\nPlease provide any additional information below.\\n'),
  ('Developer other issue report',
   'What is the issue you are reporting?\\n\\n\\nWhy are you reporting this issue?\\n\\n\\nPlease use labels and text to provide additional information.\\n')  ]


# This is the default maximum total bytes of files attached
# to all the issues in a project.
ISSUE_ATTACHMENTS_QUOTA_HARD = 50 * 1024 * 1024L
ISSUE_ATTACHMENTS_QUOTA_SOFT = ISSUE_ATTACHMENTS_QUOTA_HARD - 1 * 1024 * 1024L
