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

"""Simple class to represent the business objects that help represent
any kind of project artifact or comment.
"""

class Artifact(object):
  def __init__(self):
    self.project_name_ = ""
    self.artifact_name_ = ""
    self.docid_ = 0
    self.summary_ = ""
    self.labels_ = []
    self.creator_gaia_ = 0
    self.creation_time_ = 0
    self.modification_time_ = 0
    self.deprecated_is_deleted_ = 0
    self.deleted_by_ = 0
    self.star_count_ = 0
    self.has_project_name_ = 0
    self.has_artifact_name_ = 0
    self.has_docid_ = 0
    self.has_summary_ = 0
    self.has_creator_gaia_ = 0
    self.has_creation_time_ = 0
    self.has_modification_time_ = 0
    self.has_deprecated_is_deleted_ = 0
    self.has_deleted_by_ = 0
    self.has_star_count_ = 0

  def project_name(self): return self.project_name_

  def set_project_name(self, x):
    self.has_project_name_ = 1
    self.project_name_ = x

  def clear_project_name(self):
    self.has_project_name_ = 0
    self.project_name_ = ""

  def has_project_name(self): return self.has_project_name_

  def artifact_name(self): return self.artifact_name_

  def set_artifact_name(self, x):
    self.has_artifact_name_ = 1
    self.artifact_name_ = x

  def clear_artifact_name(self):
    self.has_artifact_name_ = 0
    self.artifact_name_ = ""

  def has_artifact_name(self): return self.has_artifact_name_

  def docid(self): return self.docid_

  def set_docid(self, x):
    self.has_docid_ = 1
    self.docid_ = x

  def clear_docid(self):
    self.has_docid_ = 0
    self.docid_ = 0

  def has_docid(self): return self.has_docid_

  def summary(self): return self.summary_

  def set_summary(self, x):
    self.has_summary_ = 1
    self.summary_ = x

  def clear_summary(self):
    self.has_summary_ = 0
    self.summary_ = ""

  def has_summary(self): return self.has_summary_

  def labels_size(self): return len(self.labels_)
  def labels_list(self): return self.labels_

  def labels(self, i):
    return self.labels_[i]

  def set_labels(self, i, x):
    self.labels_[i] = x

  def add_labels(self, x):
    self.labels_.append(x)

  def clear_labels(self):
    self.labels_ = []

  def creator_gaia(self): return self.creator_gaia_

  def set_creator_gaia(self, x):
    self.has_creator_gaia_ = 1
    self.creator_gaia_ = x

  def clear_creator_gaia(self):
    self.has_creator_gaia_ = 0
    self.creator_gaia_ = 0

  def has_creator_gaia(self): return self.has_creator_gaia_

  def creation_time(self): return self.creation_time_

  def set_creation_time(self, x):
    self.has_creation_time_ = 1
    self.creation_time_ = x

  def clear_creation_time(self):
    self.has_creation_time_ = 0
    self.creation_time_ = 0

  def has_creation_time(self): return self.has_creation_time_

  def modification_time(self): return self.modification_time_

  def set_modification_time(self, x):
    self.has_modification_time_ = 1
    self.modification_time_ = x

  def clear_modification_time(self):
    self.has_modification_time_ = 0
    self.modification_time_ = 0

  def has_modification_time(self): return self.has_modification_time_

  def deprecated_is_deleted(self): return self.deprecated_is_deleted_

  def set_deprecated_is_deleted(self, x):
    self.has_deprecated_is_deleted_ = 1
    self.deprecated_is_deleted_ = x

  def clear_deprecated_is_deleted(self):
    self.has_deprecated_is_deleted_ = 0
    self.deprecated_is_deleted_ = 0

  def has_deprecated_is_deleted(self): return self.has_deprecated_is_deleted_

  def deleted_by(self): return self.deleted_by_

  def set_deleted_by(self, x):
    self.has_deleted_by_ = 1
    self.deleted_by_ = x

  def clear_deleted_by(self):
    self.has_deleted_by_ = 0
    self.deleted_by_ = 0

  def has_deleted_by(self): return self.has_deleted_by_

  def star_count(self): return self.star_count_

  def set_star_count(self, x):
    self.has_star_count_ = 1
    self.star_count_ = x

  def clear_star_count(self):
    self.has_star_count_ = 0
    self.star_count_ = 0

  def has_star_count(self): return self.has_star_count_


class TrackedArtifact(object):
  def __init__(self):
    self.artifact_ = Artifact()
    self.status_ = ""
    self.owner_id_ = 0
    self.cc_ids_ = []
    self.has_artifact_ = 0
    self.has_status_ = 0
    self.has_owner_id_ = 0

  def artifact(self): return self.artifact_

  def mutable_artifact(self): self.has_artifact_ = 1; return self.artifact_

  def clear_artifact(self):self.has_artifact_ = 0; self.artifact_.Clear()

  def has_artifact(self): return self.has_artifact_

  def status(self): return self.status_

  def set_status(self, x):
    self.has_status_ = 1
    self.status_ = x

  def clear_status(self):
    self.has_status_ = 0
    self.status_ = ""

  def has_status(self): return self.has_status_

  def owner_id(self): return self.owner_id_

  def set_owner_id(self, x):
    self.has_owner_id_ = 1
    self.owner_id_ = x

  def clear_owner_id(self):
    self.has_owner_id_ = 0
    self.owner_id_ = 0

  def has_owner_id(self): return self.has_owner_id_

  def cc_ids_size(self): return len(self.cc_ids_)
  def cc_ids_list(self): return self.cc_ids_

  def cc_ids(self, i):
    return self.cc_ids_[i]

  def set_cc_ids(self, i, x):
    self.cc_ids_[i] = x

  def add_cc_ids(self, x):
    self.cc_ids_.append(x)

  def clear_cc_ids(self):
    self.cc_ids_ = []


class ArtifactComment_Updates(object):

  SUMMARY      =    1
  STATUS       =    2
  OWNER        =    3
  CC           =    4
  LABELS       =    5

  def __init__(self):
    self.field_ = 0
    self.newvalue_ = ""
    self.has_field_ = 0
    self.has_newvalue_ = 0

  def field(self): return self.field_

  def set_field(self, x):
    self.has_field_ = 1
    self.field_ = x

  def clear_field(self):
    self.has_field_ = 0
    self.field_ = 0

  def has_field(self): return self.has_field_

  def newvalue(self): return self.newvalue_

  def set_newvalue(self, x):
    self.has_newvalue_ = 1
    self.newvalue_ = x

  def clear_newvalue(self):
    self.has_newvalue_ = 0
    self.newvalue_ = ""

  def has_newvalue(self): return self.has_newvalue_



class ArtifactComment(object):
  def __init__(self):
    self.creator_gaia_ = 0
    self.mod_time_ = 0
    self.content_ = ""
    self.deprecated_is_deleted_ = 0
    self.deleted_by_ = 0
    self.updates_ = []
    self.has_creator_gaia_ = 0
    self.has_mod_time_ = 0
    self.has_content_ = 0
    self.has_deprecated_is_deleted_ = 0
    self.has_deleted_by_ = 0

  def creator_gaia(self): return self.creator_gaia_

  def set_creator_gaia(self, x):
    self.has_creator_gaia_ = 1
    self.creator_gaia_ = x

  def clear_creator_gaia(self):
    self.has_creator_gaia_ = 0
    self.creator_gaia_ = 0

  def has_creator_gaia(self): return self.has_creator_gaia_

  def mod_time(self): return self.mod_time_

  def set_mod_time(self, x):
    self.has_mod_time_ = 1
    self.mod_time_ = x

  def clear_mod_time(self):
    self.has_mod_time_ = 0
    self.mod_time_ = 0

  def has_mod_time(self): return self.has_mod_time_

  def content(self): return self.content_

  def set_content(self, x):
    self.has_content_ = 1
    self.content_ = x

  def clear_content(self):
    self.has_content_ = 0
    self.content_ = ""

  def has_content(self): return self.has_content_

  def deprecated_is_deleted(self): return self.deprecated_is_deleted_

  def set_deprecated_is_deleted(self, x):
    self.has_deprecated_is_deleted_ = 1
    self.deprecated_is_deleted_ = x

  def clear_deprecated_is_deleted(self):
    self.has_deprecated_is_deleted_ = 0
    self.deprecated_is_deleted_ = 0

  def has_deprecated_is_deleted(self): return self.has_deprecated_is_deleted_

  def deleted_by(self): return self.deleted_by_

  def set_deleted_by(self, x):
    self.has_deleted_by_ = 1
    self.deleted_by_ = x

  def clear_deleted_by(self):
    self.has_deleted_by_ = 0
    self.deleted_by_ = 0

  def has_deleted_by(self): return self.has_deleted_by_

  def updates_size(self): return len(self.updates_)
  def updates_list(self): return self.updates_

  def updates(self, i):
    return self.updates_[i]

  def mutable_updates(self, i):
    return self.updates_[i]

  def add_updates(self):
    x = ArtifactComment_Updates()
    self.updates_.append(x)
    return x

  def clear_updates(self):
    self.updates_ = []


class ArtifactStars(object):
  def __init__(self):
    self.starrer_gaia_ = []

  def starrer_gaia_size(self): return len(self.starrer_gaia_)
  def starrer_gaia_list(self): return self.starrer_gaia_

  def starrer_gaia(self, i):
    return self.starrer_gaia_[i]

  def set_starrer_gaia(self, i, x):
    self.starrer_gaia_[i] = x

  def add_starrer_gaia(self, x):
    self.starrer_gaia_.append(x)

  def clear_starrer_gaia(self):
    self.starrer_gaia_ = []


class UserStarsInProject(object):
  def __init__(self):
    self.artifact_names_ = []

  def artifact_names_size(self): return len(self.artifact_names_)
  def artifact_names_list(self): return self.artifact_names_

  def artifact_names(self, i):
    return self.artifact_names_[i]

  def set_artifact_names(self, i, x):
    self.artifact_names_[i] = x

  def add_artifact_names(self, x):
    self.artifact_names_.append(x)

  def clear_artifact_names(self):
    self.artifact_names_ = []
