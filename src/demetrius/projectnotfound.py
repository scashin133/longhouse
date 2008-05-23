#! /usr/bin/env python
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

"""A page hit when the user requests to see a project that does 
not exist."""

import sys

from common import post
from common import http
from common import ezt_google

import framework.helpers

from demetrius import constants
from demetrius import pageclasses
from demetrius import helpers
from demetrius import permissions

class ProjectNotFound(pageclasses.DemetriusPage):
    
    _PAGE_TEMPLATE = 'demetrius/projectnotfound.ezt'
    
    def GatherPageData(self, request, req_info):
        return {}
    
if __name__ == '__main__':
    sys.exit('This is not meant to be run as a standalone program. Exiting.')
