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

"""Simple class to represent the business objects for the issue tracker.
"""

class Issue(object):
  def __init__(self):
    self.project_name_ = ""
    self.id_ = 0
    self.summary_ = ""
    self.status_ = ""
    self.owner_id_ = 0
    self.cc_ids_ = []
    self.labels_ = []
    self.star_count_ = 0
    self.reporter_id_ = 0
    self.opened_timestamp_ = 0
    self.summary_is_escaped_ = 1
    self.closed_timestamp_ = 0
    self.modified_timestamp_ = 0
    self.has_project_name_ = 0
    self.has_id_ = 0
    self.has_summary_ = 0
    self.has_status_ = 0
    self.has_owner_id_ = 0
    self.has_star_count_ = 0
    self.has_reporter_id_ = 0
    self.has_opened_timestamp_ = 0
    self.has_summary_is_escaped_ = 0
    self.has_closed_timestamp_ = 0
    self.has_modified_timestamp_ = 0

  def project_name(self): return self.project_name_

  def set_project_name(self, x):
    self.has_project_name_ = 1
    self.project_name_ = x

  def clear_project_name(self):
    self.has_project_name_ = 0
    self.project_name_ = ""

  def has_project_name(self): return self.has_project_name_

  def id(self): return self.id_

  def set_id(self, x):
    self.has_id_ = 1
    self.id_ = x

  def clear_id(self):
    self.has_id_ = 0
    self.id_ = 0

  def has_id(self): return self.has_id_

  def summary(self): return self.summary_

  def set_summary(self, x):
    self.has_summary_ = 1
    self.summary_ = x

  def clear_summary(self):
    self.has_summary_ = 0
    self.summary_ = ""

  def has_summary(self): return self.has_summary_

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

  def star_count(self): return self.star_count_

  def set_star_count(self, x):
    self.has_star_count_ = 1
    self.star_count_ = x

  def clear_star_count(self):
    self.has_star_count_ = 0
    self.star_count_ = 0

  def has_star_count(self): return self.has_star_count_

  def reporter_id(self): return self.reporter_id_

  def set_reporter_id(self, x):
    self.has_reporter_id_ = 1
    self.reporter_id_ = x

  def clear_reporter_id(self):
    self.has_reporter_id_ = 0
    self.reporter_id_ = 0

  def has_reporter_id(self): return self.has_reporter_id_

  def opened_timestamp(self): return self.opened_timestamp_

  def set_opened_timestamp(self, x):
    self.has_opened_timestamp_ = 1
    self.opened_timestamp_ = x

  def clear_opened_timestamp(self):
    self.has_opened_timestamp_ = 0
    self.opened_timestamp_ = 0

  def has_opened_timestamp(self): return self.has_opened_timestamp_

  def summary_is_escaped(self): return self.summary_is_escaped_

  def set_summary_is_escaped(self, x):
    self.has_summary_is_escaped_ = 1
    self.summary_is_escaped_ = x

  def clear_summary_is_escaped(self):
    self.has_summary_is_escaped_ = 0
    self.summary_is_escaped_ = 1

  def has_summary_is_escaped(self): return self.has_summary_is_escaped_

  def closed_timestamp(self): return self.closed_timestamp_

  def set_closed_timestamp(self, x):
    self.has_closed_timestamp_ = 1
    self.closed_timestamp_ = x

  def clear_closed_timestamp(self):
    self.has_closed_timestamp_ = 0
    self.closed_timestamp_ = 0

  def has_closed_timestamp(self): return self.has_closed_timestamp_

  def modified_timestamp(self): return self.modified_timestamp_

  def set_modified_timestamp(self, x):
    self.has_modified_timestamp_ = 1
    self.modified_timestamp_ = x

  def clear_modified_timestamp(self):
    self.has_modified_timestamp_ = 0
    self.modified_timestamp_ = 0

  def has_modified_timestamp(self): return self.has_modified_timestamp_


class IssueComment_Updates(object):

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


class IssueComment_Attachments(object):
  def __init__(self):
    self.attachment_id_ = 0
    self.filename_ = ""
    self.filesize_ = 0
    self.mimetype_ = ""
    self.has_attachment_id_ = 0
    self.has_filename_ = 0
    self.has_filesize_ = 0
    self.has_mimetype_ = 0

  def attachment_id(self): return self.attachment_id_

  def set_attachment_id(self, x):
    self.has_attachment_id_ = 1
    self.attachment_id_ = x

  def clear_attachment_id(self):
    self.has_attachment_id_ = 0
    self.attachment_id_ = 0

  def has_attachment_id(self): return self.has_attachment_id_

  def filename(self): return self.filename_

  def set_filename(self, x):
    self.has_filename_ = 1
    self.filename_ = x

  def clear_filename(self):
    self.has_filename_ = 0
    self.filename_ = ""

  def has_filename(self): return self.has_filename_

  def filesize(self): return self.filesize_

  def set_filesize(self, x):
    self.has_filesize_ = 1
    self.filesize_ = x

  def clear_filesize(self):
    self.has_filesize_ = 0
    self.filesize_ = 0

  def has_filesize(self): return self.has_filesize_

  def mimetype(self): return self.mimetype_

  def set_mimetype(self, x):
    self.has_mimetype_ = 1
    self.mimetype_ = x

  def clear_mimetype(self):
    self.has_mimetype_ = 0
    self.mimetype_ = ""

  def has_mimetype(self): return self.has_mimetype_



class IssueComment(object):
  def __init__(self):
    self.project_name_ = ""
    self.issue_id_ = 0
    self.user_id_ = 0
    self.timestamp_ = 0
    self.content_ = ""
    self.updates_ = []
    self.deleted_by_ = 0
    self.attachments_ = []
    self.was_escaped_ = 1
    self.comment_id_ = 0
    self.has_project_name_ = 0
    self.has_issue_id_ = 0
    self.has_user_id_ = 0
    self.has_timestamp_ = 0
    self.has_content_ = 0
    self.has_deleted_by_ = 0
    self.has_was_escaped_ = 0
    self.has_comment_id_ = 0

  def project_name(self): return self.project_name_

  def set_project_name(self, x):
    self.has_project_name_ = 1
    self.project_name_ = x

  def clear_project_name(self):
    self.has_project_name_ = 0
    self.project_name_ = ""

  def has_project_name(self): return self.has_project_name_

  def issue_id(self): return self.issue_id_

  def set_issue_id(self, x):
    self.has_issue_id_ = 1
    self.issue_id_ = x

  def clear_issue_id(self):
    self.has_issue_id_ = 0
    self.issue_id_ = 0

  def has_issue_id(self): return self.has_issue_id_

  def user_id(self): return self.user_id_

  def set_user_id(self, x):
    self.has_user_id_ = 1
    self.user_id_ = x

  def clear_user_id(self):
    self.has_user_id_ = 0
    self.user_id_ = 0

  def has_user_id(self): return self.has_user_id_

  def timestamp(self): return self.timestamp_

  def set_timestamp(self, x):
    self.has_timestamp_ = 1
    self.timestamp_ = x

  def clear_timestamp(self):
    self.has_timestamp_ = 0
    self.timestamp_ = 0

  def has_timestamp(self): return self.has_timestamp_

  def content(self): return self.content_

  def set_content(self, x):
    self.has_content_ = 1
    self.content_ = x

  def clear_content(self):
    self.has_content_ = 0
    self.content_ = ""

  def has_content(self): return self.has_content_

  def updates_size(self): return len(self.updates_)
  def updates_list(self): return self.updates_

  def updates(self, i):
    return self.updates_[i]

  def mutable_updates(self, i):
    return self.updates_[i]

  def add_updates(self):
    x = IssueComment_Updates()
    self.updates_.append(x)
    return x

  def clear_updates(self):
    self.updates_ = []
  def deleted_by(self): return self.deleted_by_

  def set_deleted_by(self, x):
    self.has_deleted_by_ = 1
    self.deleted_by_ = x

  def clear_deleted_by(self):
    self.has_deleted_by_ = 0
    self.deleted_by_ = 0

  def has_deleted_by(self): return self.has_deleted_by_

  def attachments_size(self): return len(self.attachments_)
  def attachments_list(self): return self.attachments_

  def attachments(self, i):
    return self.attachments_[i]

  def mutable_attachments(self, i):
    return self.attachments_[i]

  def add_attachments(self):
    x = IssueComment_Attachments()
    self.attachments_.append(x)
    return x

  def clear_attachments(self):
    self.attachments_ = []
  def was_escaped(self): return self.was_escaped_

  def set_was_escaped(self, x):
    self.has_was_escaped_ = 1
    self.was_escaped_ = x

  def clear_was_escaped(self):
    self.has_was_escaped_ = 0
    self.was_escaped_ = 1

  def has_was_escaped(self): return self.has_was_escaped_

  def comment_id(self): return self.comment_id_

  def set_comment_id(self, x):
    self.has_comment_id_ = 1
    self.comment_id_ = x

  def clear_comment_id(self):
    self.has_comment_id_ = 0
    self.comment_id_ = 0

  def has_comment_id(self): return self.has_comment_id_


class UserIssueStars(object):
  def __init__(self):
    self.user_id_ = 0
    self.project_name_ = ""
    self.issue_ids_ = []
    self.has_user_id_ = 0
    self.has_project_name_ = 0

  def user_id(self): return self.user_id_

  def set_user_id(self, x):
    self.has_user_id_ = 1
    self.user_id_ = x

  def clear_user_id(self):
    self.has_user_id_ = 0
    self.user_id_ = 0

  def has_user_id(self): return self.has_user_id_

  def project_name(self): return self.project_name_

  def set_project_name(self, x):
    self.has_project_name_ = 1
    self.project_name_ = x

  def clear_project_name(self):
    self.has_project_name_ = 0
    self.project_name_ = ""

  def has_project_name(self): return self.has_project_name_

  def issue_ids_size(self): return len(self.issue_ids_)
  def issue_ids_list(self): return self.issue_ids_

  def issue_ids(self, i):
    return self.issue_ids_[i]

  def set_issue_ids(self, i, x):
    self.issue_ids_[i] = x

  def add_issue_ids(self, x):
    self.issue_ids_.append(x)

  def clear_issue_ids(self):
    self.issue_ids_ = []


class IssueUserStars(object):
  def __init__(self):
    self.project_name_ = ""
    self.issue_id_ = 0
    self.user_ids_ = []
    self.has_project_name_ = 0
    self.has_issue_id_ = 0

  def project_name(self): return self.project_name_

  def set_project_name(self, x):
    self.has_project_name_ = 1
    self.project_name_ = x

  def clear_project_name(self):
    self.has_project_name_ = 0
    self.project_name_ = ""

  def has_project_name(self): return self.has_project_name_

  def issue_id(self): return self.issue_id_

  def set_issue_id(self, x):
    self.has_issue_id_ = 1
    self.issue_id_ = x

  def clear_issue_id(self):
    self.has_issue_id_ = 0
    self.issue_id_ = 0

  def has_issue_id(self): return self.has_issue_id_

  def user_ids_size(self): return len(self.user_ids_)
  def user_ids_list(self): return self.user_ids_

  def user_ids(self, i):
    return self.user_ids_[i]

  def set_user_ids(self, i, x):
    self.user_ids_[i] = x

  def add_user_ids(self, x):
    self.user_ids_.append(x)

  def clear_user_ids(self):
    self.user_ids_ = []


class IssueAttachmentContent(object):
  def __init__(self):
    self.id_ = 0
    self.project_name_ = ""
    self.content_ = ""
    self.mimetype_ = ""
    self.has_id_ = 0
    self.has_project_name_ = 0
    self.has_content_ = 0
    self.has_mimetype_ = 0

  def id(self): return self.id_

  def set_id(self, x):
    self.has_id_ = 1
    self.id_ = x

  def clear_id(self):
    self.has_id_ = 0
    self.id_ = 0

  def has_id(self): return self.has_id_

  def project_name(self): return self.project_name_

  def set_project_name(self, x):
    self.has_project_name_ = 1
    self.project_name_ = x

  def clear_project_name(self):
    self.has_project_name_ = 0
    self.project_name_ = ""

  def has_project_name(self): return self.has_project_name_

  def content(self): return self.content_

  def set_content(self, x):
    self.has_content_ = 1
    self.content_ = x

  def clear_content(self):
    self.has_content_ = 0
    self.content_ = ""

  def has_content(self): return self.has_content_

  def mimetype(self): return self.mimetype_

  def set_mimetype(self, x):
    self.has_mimetype_ = 1
    self.mimetype_ = x

  def clear_mimetype(self):
    self.has_mimetype_ = 0
    self.mimetype_ = ""

  def has_mimetype(self): return self.has_mimetype_


class ProjectIssueConfig_Well_known_statuses(object):
  def __init__(self):
    self.status_ = ""
    self.means_open_ = 0
    self.status_docstring_ = ""
    self.has_status_ = 0
    self.has_means_open_ = 0
    self.has_status_docstring_ = 0

  def status(self): return self.status_

  def set_status(self, x):
    self.has_status_ = 1
    self.status_ = x

  def clear_status(self):
    self.has_status_ = 0
    self.status_ = ""

  def has_status(self): return self.has_status_

  def means_open(self): return self.means_open_

  def set_means_open(self, x):
    self.has_means_open_ = 1
    self.means_open_ = x

  def clear_means_open(self):
    self.has_means_open_ = 0
    self.means_open_ = 0

  def has_means_open(self): return self.has_means_open_

  def status_docstring(self): return self.status_docstring_

  def set_status_docstring(self, x):
    self.has_status_docstring_ = 1
    self.status_docstring_ = x

  def clear_status_docstring(self):
    self.has_status_docstring_ = 0
    self.status_docstring_ = ""

  def has_status_docstring(self): return self.has_status_docstring_



class ProjectIssueConfig_Well_known_labels(object):
  def __init__(self):
    self.label_ = ""
    self.label_docstring_ = ""
    self.has_label_ = 0
    self.has_label_docstring_ = 0

  def label(self): return self.label_

  def set_label(self, x):
    self.has_label_ = 1
    self.label_ = x

  def clear_label(self):
    self.has_label_ = 0
    self.label_ = ""

  def has_label(self): return self.has_label_

  def label_docstring(self): return self.label_docstring_

  def set_label_docstring(self, x):
    self.has_label_docstring_ = 1
    self.label_docstring_ = x

  def clear_label_docstring(self):
    self.has_label_docstring_ = 0
    self.label_docstring_ = ""

  def has_label_docstring(self): return self.has_label_docstring_



class ProjectIssueConfig_Well_known_prompts(object):
  def __init__(self):
    self.prompt_name_ = ""
    self.prompt_text_ = ""
    self.has_prompt_name_ = 0
    self.has_prompt_text_ = 0

  def prompt_name(self): return self.prompt_name_

  def set_prompt_name(self, x):
    self.has_prompt_name_ = 1
    self.prompt_name_ = x

  def clear_prompt_name(self):
    self.has_prompt_name_ = 0
    self.prompt_name_ = ""

  def has_prompt_name(self): return self.has_prompt_name_

  def prompt_text(self): return self.prompt_text_

  def set_prompt_text(self, x):
    self.has_prompt_text_ = 1
    self.prompt_text_ = x

  def clear_prompt_text(self):
    self.has_prompt_text_ = 0
    self.prompt_text_ = ""

  def has_prompt_text(self): return self.has_prompt_text_


class ProjectIssueConfig_Canned_queries(object):
  def __init__(self):
    self.name_ = ""
    self.mustang_query_ = ""
    self.has_name_ = 0
    self.has_mustang_query_ = 0

  def name(self): return self.name_

  def set_name(self, x):
    self.has_name_ = 1
    self.name_ = x

  def clear_name(self):
    self.has_name_ = 0
    self.name_ = ""

  def has_name(self): return self.has_name_

  def mustang_query(self): return self.mustang_query_

  def set_mustang_query(self, x):
    self.has_mustang_query_ = 1
    self.mustang_query_ = x

  def clear_mustang_query(self):
    self.has_mustang_query_ = 0
    self.mustang_query_ = ""

  def has_mustang_query(self): return self.has_mustang_query_


class ProjectIssueConfig(object):
  def __init__(self):
    self.project_name_ = ""
    self.well_known_statuses_ = []
    self.well_known_labels_ = []
    self.exclusive_label_prefixes_ = []
    self.well_known_prompts_ = []
    self.default_prompt_for_developers_ = 0
    self.default_prompt_for_users_ = 0
    self.canned_queries_ = []
    self.default_col_spec_ = ""
    self.default_sort_spec_ = ""
    self.default_x_attr_ = ""
    self.default_y_attr_ = ""
    self.has_project_name_ = 0
    self.has_default_prompt_for_developers_ = 0
    self.has_default_prompt_for_users_ = 0
    self.has_default_col_spec_ = 0
    self.has_default_sort_spec_ = 0
    self.has_default_x_attr_ = 0
    self.has_default_y_attr_ = 0

  def project_name(self): return self.project_name_

  def set_project_name(self, x):
    self.has_project_name_ = 1
    self.project_name_ = x

  def clear_project_name(self):
    self.has_project_name_ = 0
    self.project_name_ = ""

  def has_project_name(self): return self.has_project_name_

  def well_known_statuses_size(self): return len(self.well_known_statuses_)
  def well_known_statuses_list(self): return self.well_known_statuses_

  def well_known_statuses(self, i):
    return self.well_known_statuses_[i]

  def mutable_well_known_statuses(self, i):
    return self.well_known_statuses_[i]

  def add_well_known_statuses(self):
    x = ProjectIssueConfig_Well_known_statuses()
    self.well_known_statuses_.append(x)
    return x

  def clear_well_known_statuses(self):
    self.well_known_statuses_ = []
  def well_known_labels_size(self): return len(self.well_known_labels_)
  def well_known_labels_list(self): return self.well_known_labels_

  def well_known_labels(self, i):
    return self.well_known_labels_[i]

  def mutable_well_known_labels(self, i):
    return self.well_known_labels_[i]

  def add_well_known_labels(self):
    x = ProjectIssueConfig_Well_known_labels()
    self.well_known_labels_.append(x)
    return x

  def clear_well_known_labels(self):
    self.well_known_labels_ = []
  def exclusive_label_prefixes_size(self): return len(self.exclusive_label_prefixes_)
  def exclusive_label_prefixes_list(self): return self.exclusive_label_prefixes_

  def exclusive_label_prefixes(self, i):
    return self.exclusive_label_prefixes_[i]

  def set_exclusive_label_prefixes(self, i, x):
    self.exclusive_label_prefixes_[i] = x

  def add_exclusive_label_prefixes(self, x):
    self.exclusive_label_prefixes_.append(x)

  def clear_exclusive_label_prefixes(self):
    self.exclusive_label_prefixes_ = []

  def well_known_prompts_size(self): return len(self.well_known_prompts_)
  def well_known_prompts_list(self): return self.well_known_prompts_

  def well_known_prompts(self, i):
    return self.well_known_prompts_[i]

  def mutable_well_known_prompts(self, i):
    return self.well_known_prompts_[i]

  def add_well_known_prompts(self):
    x = ProjectIssueConfig_Well_known_prompts()
    self.well_known_prompts_.append(x)
    return x

  def clear_well_known_prompts(self):
    self.well_known_prompts_ = []
  def default_prompt_for_developers(self): return self.default_prompt_for_developers_

  def set_default_prompt_for_developers(self, x):
    self.has_default_prompt_for_developers_ = 1
    self.default_prompt_for_developers_ = x

  def clear_default_prompt_for_developers(self):
    self.has_default_prompt_for_developers_ = 0
    self.default_prompt_for_developers_ = 0

  def has_default_prompt_for_developers(self): return self.has_default_prompt_for_developers_

  def default_prompt_for_users(self): return self.default_prompt_for_users_

  def set_default_prompt_for_users(self, x):
    self.has_default_prompt_for_users_ = 1
    self.default_prompt_for_users_ = x

  def clear_default_prompt_for_users(self):
    self.has_default_prompt_for_users_ = 0
    self.default_prompt_for_users_ = 0

  def has_default_prompt_for_users(self): return self.has_default_prompt_for_users_

  def canned_queries_size(self): return len(self.canned_queries_)
  def canned_queries_list(self): return self.canned_queries_

  def canned_queries(self, i):
    return self.canned_queries_[i]

  def mutable_canned_queries(self, i):
    return self.canned_queries_[i]

  def add_canned_queries(self):
    x = ProjectIssueConfig_Canned_queries()
    self.canned_queries_.append(x)
    return x

  def clear_canned_queries(self):
    self.canned_queries_ = []
  def default_col_spec(self): return self.default_col_spec_

  def set_default_col_spec(self, x):
    self.has_default_col_spec_ = 1
    self.default_col_spec_ = x

  def clear_default_col_spec(self):
    self.has_default_col_spec_ = 0
    self.default_col_spec_ = ""

  def has_default_col_spec(self): return self.has_default_col_spec_

  def default_sort_spec(self): return self.default_sort_spec_

  def set_default_sort_spec(self, x):
    self.has_default_sort_spec_ = 1
    self.default_sort_spec_ = x

  def clear_default_sort_spec(self):
    self.has_default_sort_spec_ = 0
    self.default_sort_spec_ = ""

  def has_default_sort_spec(self): return self.has_default_sort_spec_

  def default_x_attr(self): return self.default_x_attr_

  def set_default_x_attr(self, x):
    self.has_default_x_attr_ = 1
    self.default_x_attr_ = x

  def clear_default_x_attr(self):
    self.has_default_x_attr_ = 0
    self.default_x_attr_ = ""

  def has_default_x_attr(self): return self.has_default_x_attr_

  def default_y_attr(self): return self.default_y_attr_

  def set_default_y_attr(self, x):
    self.has_default_y_attr_ = 1
    self.default_y_attr_ = x

  def clear_default_y_attr(self):
    self.has_default_y_attr_ = 0
    self.default_y_attr_ = ""

  def has_default_y_attr(self): return self.has_default_y_attr_
