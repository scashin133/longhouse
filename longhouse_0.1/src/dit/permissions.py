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

"""Permissions for the Demetrius Issue Tracker.

See demetrius/permissions.py for more info on permissions.

"""

from bo import demetrius_pb
import demetrius.permissions


ENTER_METADATA = 'enter_metadata'
ENTER_COMMENT = 'enter_comment'
SET_STAR = 'set_star'
EDIT_DESCRIPTION = 'edit_description'
EDIT_ANY_COMMENT = 'edit_any_comment'

DIT_PERMISSIONS = {
  (demetrius.permissions.ADMIN_ROLE,
   demetrius.permissions.WILDCARD_PROJECT_STATUS):
    demetrius.permissions.PermissionSet([
      ENTER_METADATA, ENTER_COMMENT, SET_STAR, EDIT_DESCRIPTION,
      EDIT_ANY_COMMENT, demetrius.permissions.DELETE_ANY]),

  (demetrius.permissions.OWNER_ROLE, demetrius_pb.Project.LIVE):
    demetrius.permissions.PermissionSet([
      ENTER_METADATA, ENTER_COMMENT, SET_STAR,
      demetrius.permissions.DELETE_ANY]),

  (demetrius.permissions.OWNER_ROLE, demetrius_pb.Project.HIDDEN):
    demetrius.permissions.PermissionSet([
      ENTER_METADATA, ENTER_COMMENT, SET_STAR,
      demetrius.permissions.DELETE_ANY]),

  (demetrius.permissions.OWNER_ROLE, demetrius_pb.Project.SECURE):
    demetrius.permissions.PermissionSet([
      ENTER_METADATA, ENTER_COMMENT, SET_STAR,
      demetrius.permissions.DELETE_ANY]),

  (demetrius.permissions.MEMBER_ROLE, demetrius_pb.Project.LIVE):
    demetrius.permissions.PermissionSet([
      ENTER_METADATA, ENTER_COMMENT, SET_STAR,
      demetrius.permissions.DELETE_OWN]),

  (demetrius.permissions.MEMBER_ROLE, demetrius_pb.Project.HIDDEN):
    demetrius.permissions.PermissionSet([
      ENTER_METADATA, ENTER_COMMENT, SET_STAR,
      demetrius.permissions.DELETE_OWN]),

  (demetrius.permissions.MEMBER_ROLE, demetrius_pb.Project.SECURE):
    demetrius.permissions.PermissionSet([
      ENTER_METADATA, ENTER_COMMENT, SET_STAR,
      demetrius.permissions.DELETE_OWN]),

  (demetrius.permissions.GMAIL_USER_ROLE, demetrius_pb.Project.LIVE):
    demetrius.permissions.PermissionSet([
      ENTER_COMMENT, SET_STAR, demetrius.permissions.DELETE_OWN]),

  (demetrius.permissions.USER_ROLE, demetrius_pb.Project.LIVE):
    demetrius.permissions.PermissionSet([
      ENTER_COMMENT, SET_STAR, demetrius.permissions.DELETE_OWN]),

  # anon users can only view issues

  }
