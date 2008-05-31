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

"""Some constants used by demetrius servlets.
"""

import sys
import re
import string

import framework.constants

# TODO: come up with a real default doom constants
DEFAULT_DOOM_REASON = "Because it is."
DEFAULT_DOOM_PERIOD = 3

# Default number of project search results per pagination page.
DEFAULT_RESULTS_PER_PAGE = 10
MAXIMUM_RESULT_PAGES_OFFERED = 10

# Default number of members shown per page. Also, max shown on summary page.
MEMBERS_PER_PAGE = 50

# CSS classes to use on the <body> element to make each of main tabs highlight.
MAIN_TAB_NONE = 't0'
MAIN_TAB_SUMMARY = 't1'
MAIN_TAB_DOWNLOADS = 't2'
MAIN_TAB_ISSUES = 't3'
MAIN_TAB_SOURCE = 't4'
MAIN_TAB_ADMIN = 't5'
MAIN_TAB_WIKI = 't6'

# CSS classes for the <body> element to make each of admin tabs highlight.
ADMIN_TAB_META = 'st1'
ADMIN_TAB_MEMBERS = 'st2'
ADMIN_TAB_ISSUES = 'st3'
ADMIN_TAB_ADVANCED = 'st4'
ADMIN_TAB_DOWNLOADS = 'st5'
ADMIN_TAB_WIKI = 'st6'
ADMIN_TAB_PERSIST = 'st7'
ADMIN_TAB_PORTAL = 'st8'

# URLs of site-wide static demetrius pages
HOSTING_HOME_URL = '/'  # the big search box w/ popular labels

# URLs for login pages
LOGIN_PAGE_URL = '/login'
LOGIN_FORM_URL = '/login.do'
LOGOUT_PAGE_URL = '/logout'

# URLs for account registration
REGISTRATION_PAGE_URL = '/createAccount'
REGISTRATION_FORM_URL = '/createAccount.do'
VALIDATION_PAGE_URL = '/validateAccount'
VALIDATION_FORM_URL = '/validateAccount.do'

# URL for user profile & settings pages
USER_PROFILE_PAGE_URL = '/'
USER_SETTINGS_PAGE_URL = '/hosting/settings'

# URLs of site-wide demetrius pages
PROJECT_CREATE_PAGE_URL = '/hosting/createProject'
PROJECT_CREATE_FORM_URL = '/hosting/createProject.do'

# URLs for other site sections, to use for placeholder pages
DOWNLOADS_INDEX_URL = '/downloads/list'
WIKI_INDEX_URL = '/w/list'
SEARCH_PAGE_URL = '/hosting/search'
ADMIN_DOWNLOADS_PAGE_URL = '/adminDownloads'
ADMIN_WIKI_PAGE_URL = '/adminWiki'

# URLs of demetrius project pages
SUMMARY_PAGE_URL = '/'
PEOPLE_PAGE_URL = '/people'
ADMIN_PORTAL_PAGE_URL = '/adminPortal'
ADMIN_META_PAGE_URL = '/admin'
ADMIN_META_FORM_URL = '/admin.do'
ADMIN_PERSIST_PAGE_URL = '/adminPersist'
ADMIN_PERSIST_FORM_URL = '/adminPersist.do'
ADMIN_MEMBERS_PAGE_URL = '/adminMembers'
ADMIN_MEMBERS_FORM_URL = '/adminMembers.do'
ADMIN_ADVANCED_PAGE_URL = '/adminAdvanced'
ADMIN_ADVANCED_FORM_URL = '/adminAdvanced.do'
PROJECT_MEMBERS_FEED_URL = '/feeds/projectMembers'
SOURCE_PAGE_URL = '/source'

# URL for projectnotfound page
PROJECT_NOT_FOUND_URL = '/projectnotfound'

# URLs of demetrius static content like images and client-side includes.
# These are found under googledata/codesite/html and served under /hosting/...
DEMETRIUS_STATIC_CONTENT = [
  '/images/ul.gif', '/images/ur.gif', '/images/ll.gif', '/images/lr.gif',
  '/images/dl_arrow.gif', '/images/downarrow.gif', '/images/triangle.gif',
  '/images/code_sm.png', '/images/star_on.gif', '/images/star_off.gif',
  '/images/paperclip.gif', '/images/generic.gif', '/images/tearoff_icon.gif',
  '/images/plus.gif', '/images/minus.gif',
  '/css/d_20070828.css', '/css/d_ie.css',
  '/js/prettify.js',
  ]

# Regular expression for a user name.
# TODO: Compare to AuthSub's definition of acceptable username chars.
RE_USERNAME = re.compile(r'[._a-zA-Z0-9]+')

# Limits on the amount of metadata that a user is allowed to have on
# a project.
# TODO: allow an optional value in the Project BO to
# override this value for that project.
MAX_PROJECT_LABELS = 20
MAX_PROJECT_LINKS = 20
MAX_PROJECT_GROUPS = 20
MAX_PROJECT_BLOGS = 20
MAX_PROJECT_PEOPLE = 50

# Placeholder values in artifact entry forms that must be changed before
# the form can be submitted.
PROMPT_SUMMARY = 'Enter one-line summary'

MIN_PROJECT_NAME_LENGTH = 3
MAX_PROJECT_NAME_LENGTH = 50

# Pattern to match a valid project name.  Users of this pattern MUST use
# the re.VERBOSE flag or the whitespace and comments we be considered
# significant and the pattern will not work.  See "re" module documentation.
RE_PROJECT_NAME_PATTERN_VERBOSE = r"""
  (?=[-a-z0-9]*[a-z][-a-z0-9]*)   # Lookahead to make sure there is at least
                                  # one letter in the whole name.
  [a-z0-9]                        # Start with a letter or digit.
  [-a-z0-9]{%d,%d}                # Follow with (min-1) to (max-1) number of
                                  # valid characters.
""" % (MIN_PROJECT_NAME_LENGTH-1, MAX_PROJECT_NAME_LENGTH-1)

# Compiled regexp to match the project name and nothing more before or after.
RE_PROJECT_NAME = re.compile('^%s$' % RE_PROJECT_NAME_PATTERN_VERBOSE,
    re.VERBOSE)

if __name__ == '__main__':
  sys.exit('this is not meant to be run as a standalone program. Exiting.')
