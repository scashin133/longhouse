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

"""Utility functions for accessing a User business object.
"""

import random
import os

from bo import demetrius_pb

from framework import constants


def MakeAuthSubClient():
  """Return a client object, required for authentication requests."""
  return None  # TODO(students)


def UsernameToID(client, username):
  """Return the 64bit user ID of username@gmail.com.

  If an error occurs, or the username doesn't exist, return None.
  """
  return EmailToID(client, username + '@gmail.com')


def EmailToID(client, email):
  """Return the 64bit user ID of username@gmail.com.

  If an error occurs, or the username doesn't exist, return None.
  """
  # TODO(students) use AuthSub
  return 0

def GetUserPrefs(client, id):
  """Return User business object that has prefs.

  If an error occurs, or the BO is not available, return None.
  """
  # TODO(students)
  return None



def GetUsername(user_id, conn_pool):
  """Return just the username for the user with the given user id."""
  # TODO(students)
  return 'username'


def GetDisplayName(user_id, conn_pool):
  """Return a display name for the user with the given user id."""
  if user_id == constants.NO_USER_SPECIFIED:
    return constants.NO_USER_NAME

  email = conn_pool.GetUserEmail(user_id)
  if email is None:
    return framework.constants.NO_USER_NAME

  username, user_domain = email.split('@')
  if user_domain in  ['gmail.com', 'googlemail.com']:
    return username

  obscured_email = ('%s...@%s' %
    (username[0 : min(8, max(1, len(username) - 3))], user_domain))
  return obscured_email


def GetUsernameAndDomain(user_id, conn_pool):
  """Return the user's name and email domain."""
  if user_id == framework.constants.NO_USER_SPECIFIED:
    return framework.constants.NO_USER_NAME, None

  email = conn_pool.GetUserEmail(user_id)
  if email is None:
    return framework.constants.NO_USER_NAME, None
  else:
    return email.split('@')

def GenerateSVNPassword():
	password = ""
	
	for i in range(10):
		password = password + str(random.randint(0,9))
	return password
