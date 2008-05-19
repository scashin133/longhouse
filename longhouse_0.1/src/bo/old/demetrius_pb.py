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

import thread

"""Simple class to represent the business objects for project
workspaces and users.
"""


class Project_LinksURL(object):
  def __init__(self):
    self.label_ = ""
    self.url_ = ""
    self.has_label_ = 0
    self.has_url_ = 0

  def label(self): return self.label_

  def set_label(self, x):
    self.has_label_ = 1
    self.label_ = x

  def clear_label(self):
    self.has_label_ = 0
    self.label_ = ""

  def has_label(self): return self.has_label_

  def url(self): return self.url_

  def set_url(self, x):
    self.has_url_ = 1
    self.url_ = x

  def clear_url(self):
    self.has_url_ = 0
    self.url_ = ""

  def has_url(self): return self.has_url_


class Project_LinksBlog(object):
  def __init__(self):
    self.label_ = ""
    self.url_ = ""
    self.feed_ = ""
    self.has_label_ = 0
    self.has_url_ = 0
    self.has_feed_ = 0

  def label(self): return self.label_

  def set_label(self, x):
    self.has_label_ = 1
    self.label_ = x

  def clear_label(self):
    self.has_label_ = 0
    self.label_ = ""

  def has_label(self): return self.has_label_

  def url(self): return self.url_

  def set_url(self, x):
    self.has_url_ = 1
    self.url_ = x

  def clear_url(self):
    self.has_url_ = 0
    self.url_ = ""

  def has_url(self): return self.has_url_

  def feed(self): return self.feed_

  def set_feed(self, x):
    self.has_feed_ = 1
    self.feed_ = x

  def clear_feed(self):
    self.has_feed_ = 0
    self.feed_ = ""

  def has_feed(self): return self.has_feed_


class Project_LinksGroup(object):
  def __init__(self):
    self.group_name_ = ""
    self.label_ = ""
    self.has_group_name_ = 0
    self.has_label_ = 0

  def group_name(self): return self.group_name_

  def set_group_name(self, x):
    self.has_group_name_ = 1
    self.group_name_ = x

  def clear_group_name(self):
    self.has_group_name_ = 0
    self.group_name_ = ""

  def has_group_name(self): return self.has_group_name_

  def label(self): return self.label_

  def set_label(self, x):
    self.has_label_ = 1
    self.label_ = x

  def clear_label(self):
    self.has_label_ = 0
    self.label_ = ""

  def has_label(self): return self.has_label_



class Project_LinksIssues(object):
  def __init__(self):
    self.query_name_ = ""
    self.has_query_name_ = 0

  def query_name(self): return self.query_name_

  def set_query_name(self, x):
    self.has_query_name_ = 1
    self.query_name_ = x

  def clear_query_name(self):
    self.has_query_name_ = 0
    self.query_name_ = ""

  def has_query_name(self): return self.has_query_name_



class Project(object):

  LIVE         =    1
  DELETE_PENDING =    2
  MOVED        =    3
  DOOMED       =    4
  HIDDEN       =    5
  SECURE       =    6
  LOCKED       =    7

  def __init__(self):
    self.state_ = 0
    self.project_name_ = ""
    self.project_num_ = 0
    self.repository_url_ = ""
    self.summary_ = ""
    self.description_ = ""
    self.license_key_ = ""
    self.labels_ = []
    self.delete_reason_ = ""
    self.delete_time_ = 0
    self.owner_ids_ = []
    self.member_ids_ = []
    self.commit_notify_address_ = ""
    self.issue_notify_address_ = ""
    self.linksurl_ = []
    self.linksblog_ = []
    self.linksgroup_ = []
    self.linksissues_ = []
    self.analytics_account_ = ""
    self.attachment_bytes_used_ = 0
    self.attachment_quota_ = 0
    self.recent_activity_ = 0
    self.download_bytes_used_ = 0
    self.download_quota_ = 0
    self.max_upload_size_ = 0
    self.wikiize_description_ = 0
    self.has_state_ = 0
    self.has_project_name_ = 0
    self.has_project_num_ = 0
    self.has_summary_ = 0
    self.has_description_ = 0
    self.has_license_key_ = 0
    self.has_delete_reason_ = 0
    self.has_delete_time_ = 0
    self.has_commit_notify_address_ = 0
    self.has_issue_notify_address_ = 0
    self.has_analytics_account_ = 0
    self.has_attachment_bytes_used_ = 0
    self.has_attachment_quota_ = 0
    self.has_recent_activity_ = 0
    self.has_download_bytes_used_ = 0
    self.has_download_quota_ = 0
    self.has_max_upload_size_ = 0
    self.has_wikiize_description_ = 0

  def state(self): return self.state_

  def set_state(self, x):
    self.has_state_ = 1
    self.state_ = x

  def clear_state(self):
    self.has_state_ = 0
    self.state_ = 0

  def has_state(self): return self.has_state_

  def project_name(self): return self.project_name_

  def set_project_name(self, x):
    self.has_project_name_ = 1
    self.project_name_ = x

  def clear_project_name(self):
    self.has_project_name_ = 0
    self.project_name_ = ""

  def has_project_name(self): return self.has_project_name_

  def project_num(self): return self.project_num_

  def set_project_num(self, x):
    self.has_project_num_ = 1
    self.project_num_ = x

  def clear_project_num(self):
    self.has_project_num_ = 0
    self.project_num_ = 0

  def has_project_num(self): return self.has_project_num_

  def has_repository_url(self): return self.repository_url_ is ''
  
  def set_repository_url(self, url):
      self.repository_url_ = url

  def repository_url(self):
      return self.repository_url_

  def summary(self): return self.summary_

  def set_summary(self, x):
    self.has_summary_ = 1
    self.summary_ = x

  def clear_summary(self):
    self.has_summary_ = 0
    self.summary_ = ""

  def has_summary(self): return self.has_summary_

  def description(self): return self.description_

  def set_description(self, x):
    self.has_description_ = 1
    self.description_ = x

  def clear_description(self):
    self.has_description_ = 0
    self.description_ = ""

  def has_description(self): return self.has_description_

  def license_key(self): return self.license_key_

  def set_license_key(self, x):
    self.has_license_key_ = 1
    self.license_key_ = x

  def clear_license_key(self):
    self.has_license_key_ = 0
    self.license_key_ = ""

  def has_license_key(self): return self.has_license_key_

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

  def delete_reason(self): return self.delete_reason_

  def set_delete_reason(self, x):
    self.has_delete_reason_ = 1
    self.delete_reason_ = x

  def clear_delete_reason(self):
    self.has_delete_reason_ = 0
    self.delete_reason_ = ""

  def has_delete_reason(self): return self.has_delete_reason_

  def delete_time(self): return self.delete_time_

  def set_delete_time(self, x):
    self.has_delete_time_ = 1
    self.delete_time_ = x

  def clear_delete_time(self):
    self.has_delete_time_ = 0
    self.delete_time_ = 0

  def has_delete_time(self): return self.has_delete_time_

  def owner_ids_size(self): return len(self.owner_ids_)
  def owner_ids_list(self): return self.owner_ids_

  def owner_ids(self, i):
    return self.owner_ids_[i]

  def set_owner_ids(self, i, x):
    self.owner_ids_[i] = x

  def add_owner_ids(self, x):
    self.owner_ids_.append(x)

  def clear_owner_ids(self):
    self.owner_ids_ = []

  def member_ids_size(self): return len(self.member_ids_)
  def member_ids_list(self): return self.member_ids_

  def member_ids(self, i):
    return self.member_ids_[i]

  def set_member_ids(self, i, x):
    self.member_ids_[i] = x

  def add_member_ids(self, x):
    self.member_ids_.append(x)

  def clear_member_ids(self):
    self.member_ids_ = []

  def commit_notify_address(self): return self.commit_notify_address_

  def set_commit_notify_address(self, x):
    self.has_commit_notify_address_ = 1
    self.commit_notify_address_ = x

  def clear_commit_notify_address(self):
    self.has_commit_notify_address_ = 0
    self.commit_notify_address_ = ""

  def has_commit_notify_address(self): return self.has_commit_notify_address_

  def issue_notify_address(self): return self.issue_notify_address_

  def set_issue_notify_address(self, x):
    self.has_issue_notify_address_ = 1
    self.issue_notify_address_ = x

  def clear_issue_notify_address(self):
    self.has_issue_notify_address_ = 0
    self.issue_notify_address_ = ""

  def has_issue_notify_address(self): return self.has_issue_notify_address_

  def linksurl_size(self): return len(self.linksurl_)
  def linksurl_list(self): return self.linksurl_

  def linksurl(self, i):
    return self.linksurl_[i]

  def mutable_linksurl(self, i):
    return self.linksurl_[i]

  def add_linksurl(self):
    x = Project_LinksURL()
    self.linksurl_.append(x)
    return x

  def clear_linksurl(self):
    self.linksurl_ = []
  def linksblog_size(self): return len(self.linksblog_)
  def linksblog_list(self): return self.linksblog_

  def linksblog(self, i):
    return self.linksblog_[i]

  def mutable_linksblog(self, i):
    return self.linksblog_[i]

  def add_linksblog(self):
    x = Project_LinksBlog()
    self.linksblog_.append(x)
    return x

  def clear_linksblog(self):
    self.linksblog_ = []
  def linksgroup_size(self): return len(self.linksgroup_)
  def linksgroup_list(self): return self.linksgroup_

  def linksgroup(self, i):
    return self.linksgroup_[i]

  def mutable_linksgroup(self, i):
    return self.linksgroup_[i]

  def add_linksgroup(self):
    x = Project_LinksGroup()
    self.linksgroup_.append(x)
    return x

  def clear_linksgroup(self):
    self.linksgroup_ = []
  def linksissues_size(self): return len(self.linksissues_)
  def linksissues_list(self): return self.linksissues_

  def linksissues(self, i):
    return self.linksissues_[i]

  def mutable_linksissues(self, i):
    return self.linksissues_[i]

  def add_linksissues(self):
    x = Project_LinksIssues()
    self.linksissues_.append(x)
    return x

  def clear_linksissues(self):
    self.linksissues_ = []
  def analytics_account(self): return self.analytics_account_

  def set_analytics_account(self, x):
    self.has_analytics_account_ = 1
    self.analytics_account_ = x

  def clear_analytics_account(self):
    self.has_analytics_account_ = 0
    self.analytics_account_ = ""

  def has_analytics_account(self): return self.has_analytics_account_

  def attachment_bytes_used(self): return self.attachment_bytes_used_

  def set_attachment_bytes_used(self, x):
    self.has_attachment_bytes_used_ = 1
    self.attachment_bytes_used_ = x

  def clear_attachment_bytes_used(self):
    self.has_attachment_bytes_used_ = 0
    self.attachment_bytes_used_ = 0

  def has_attachment_bytes_used(self): return self.has_attachment_bytes_used_

  def attachment_quota(self): return self.attachment_quota_

  def set_attachment_quota(self, x):
    self.has_attachment_quota_ = 1
    self.attachment_quota_ = x

  def clear_attachment_quota(self):
    self.has_attachment_quota_ = 0
    self.attachment_quota_ = 0

  def has_attachment_quota(self): return self.has_attachment_quota_

  def recent_activity(self): return self.recent_activity_

  def set_recent_activity(self, x):
    self.has_recent_activity_ = 1
    self.recent_activity_ = x

  def clear_recent_activity(self):
    self.has_recent_activity_ = 0
    self.recent_activity_ = 0

  def has_recent_activity(self): return self.has_recent_activity_

  def download_bytes_used(self): return self.download_bytes_used_

  def set_download_bytes_used(self, x):
    self.has_download_bytes_used_ = 1
    self.download_bytes_used_ = x

  def clear_download_bytes_used(self):
    self.has_download_bytes_used_ = 0
    self.download_bytes_used_ = 0

  def has_download_bytes_used(self): return self.has_download_bytes_used_

  def download_quota(self): return self.download_quota_

  def set_download_quota(self, x):
    self.has_download_quota_ = 1
    self.download_quota_ = x

  def clear_download_quota(self):
    self.has_download_quota_ = 0
    self.download_quota_ = 0

  def has_download_quota(self): return self.has_download_quota_

  def max_upload_size(self): return self.max_upload_size_

  def set_max_upload_size(self, x):
    self.has_max_upload_size_ = 1
    self.max_upload_size_ = x

  def clear_max_upload_size(self):
    self.has_max_upload_size_ = 0
    self.max_upload_size_ = 0

  def has_max_upload_size(self): return self.has_max_upload_size_

  def wikiize_description(self): return self.wikiize_description_

  def set_wikiize_description(self, x):
    self.has_wikiize_description_ = 1
    self.wikiize_description_ = x

  def clear_wikiize_description(self):
    self.has_wikiize_description_ = 0
    self.wikiize_description_ = 0

  def has_wikiize_description(self): return self.has_wikiize_description_

  def __str__(self):
	project_string_list = []
	project_string_list.append("Project Name: " + str(self.project_name()))
	project_string_list.append("Project State: " + str(self.state()))
	project_string_list.append("Project Summary: " + str(self.summary()))
	project_string_list.append("Project Description: " + str(self.description()))
	project_string_list.append("Project Labels: " + str(self.labels_list()))
	project_string_list.append("Project Owner Size: " + str(self.owner_ids_size()))
	return "\n".join(project_string_list)

class User(object):
  def __init__(self):
    self.owner_of_projects_ = []
    self.member_of_projects_ = []
    self.acct_email_ = ""
    self.acct_username_ = ""
    self.acct_password_ = ""
    self.svn_password_ = ""
    self.is_site_admin_ = 0
    self.notify_issue_change_ = 1
    self.notify_starred_issue_change_ = 1
    self.banned_ = ""
    self.project_creation_limit_ = None
    self.issue_comment_limit_ = None
    self.issue_attachment_limit_ = None
    self.issue_bulk_edit_limit_ = None
    self.upload_limit_ = None
    self.keep_wiki_help_open_ = 0
    self.keep_wiki_log_open_ = 0
    self.has_svn_password_ = 0
    self.has_is_site_admin_ = 0
    self.has_notify_issue_change_ = 0
    self.has_notify_starred_issue_change_ = 0
    self.has_banned_ = 0
    self.has_project_creation_limit_ = 0
    self.has_issue_comment_limit_ = 0
    self.has_issue_attachment_limit_ = 0
    self.has_issue_bulk_edit_limit_ = 0
    self.has_upload_limit_ = 0
    self.has_keep_wiki_help_open_ = 0
    self.has_keep_wiki_log_open_ = 0
    self.lazy_init_lock_ = thread.allocate_lock()

  def owner_of_projects_size(self): return len(self.owner_of_projects_)
  def owner_of_projects_list(self): return self.owner_of_projects_

  def owner_of_projects(self, i):
    return self.owner_of_projects_[i]

  def set_owner_of_projects(self, i, x):
    self.owner_of_projects_[i] = x

  def add_owner_of_projects(self, x):
    self.owner_of_projects_.append(x)

  def clear_owner_of_projects(self):
    self.owner_of_projects_ = []

  def set_account_username(self, u):
    self.acct_username_ = u
    
  def get_account_username(self):  
    return self.acct_username_

  def set_account_password(self, p):
    self.acct_password_ = p
    
  def verify_account_password(self, p):  
    if self.acct_password_ == p:
      return True
    else:
      return False
    
  def get_account_email(self):
    return self.acct_email_

  def set_account_email(self, email):
    self.acct_email_ = email
    
  def member_of_projects_size(self): return len(self.member_of_projects_)
  def member_of_projects_list(self): return self.member_of_projects_

  def member_of_projects(self, i):
    return self.member_of_projects_[i]

  def set_member_of_projects(self, i, x):
    self.member_of_projects_[i] = x

  def add_member_of_projects(self, x):
    self.member_of_projects_.append(x)

  def clear_member_of_projects(self):
    self.member_of_projects_ = []

  def svn_password(self): return self.svn_password_

  def set_svn_password(self, x):
    self.has_svn_password_ = 1
    self.svn_password_ = x

  def clear_svn_password(self):
    self.has_svn_password_ = 0
    self.svn_password_ = ""

  def has_svn_password(self): return self.has_svn_password_

  def is_site_admin(self): return self.is_site_admin_

  def set_is_site_admin(self, x):
    self.has_is_site_admin_ = 1
    self.is_site_admin_ = x

  def clear_is_site_admin(self):
    self.has_is_site_admin_ = 0
    self.is_site_admin_ = 0

  def has_is_site_admin(self): return self.has_is_site_admin_

  def notify_issue_change(self): return self.notify_issue_change_

  def set_notify_issue_change(self, x):
    self.has_notify_issue_change_ = 1
    self.notify_issue_change_ = x

  def clear_notify_issue_change(self):
    self.has_notify_issue_change_ = 0
    self.notify_issue_change_ = 1

  def has_notify_issue_change(self): return self.has_notify_issue_change_

  def notify_starred_issue_change(self): return self.notify_starred_issue_change_

  def set_notify_starred_issue_change(self, x):
    self.has_notify_starred_issue_change_ = 1
    self.notify_starred_issue_change_ = x

  def clear_notify_starred_issue_change(self):
    self.has_notify_starred_issue_change_ = 0
    self.notify_starred_issue_change_ = 1

  def has_notify_starred_issue_change(self): return self.has_notify_starred_issue_change_

  def banned(self): return self.banned_

  def set_banned(self, x):
    self.has_banned_ = 1
    self.banned_ = x

  def clear_banned(self):
    self.has_banned_ = 0
    self.banned_ = ""

  def has_banned(self): return self.has_banned_

  def project_creation_limit(self):
    if self.project_creation_limit_ is None:
      self.lazy_init_lock_.acquire()
      try:
        if self.project_creation_limit_ is None: self.project_creation_limit_ = ActionLimit()
      finally:
        self.lazy_init_lock_.release()
    return self.project_creation_limit_

  def mutable_project_creation_limit(self): self.has_project_creation_limit_ = 1; return self.project_creation_limit()

  def clear_project_creation_limit(self):
    #Warning: this method does not acquire the lock.
    self.has_project_creation_limit_ = 0;
    if self.project_creation_limit_ is not None: self.project_creation_limit_.Clear()

  def has_project_creation_limit(self): return self.has_project_creation_limit_

  def issue_comment_limit(self):
    if self.issue_comment_limit_ is None:
      self.lazy_init_lock_.acquire()
      try:
        if self.issue_comment_limit_ is None: self.issue_comment_limit_ = ActionLimit()
      finally:
        self.lazy_init_lock_.release()
    return self.issue_comment_limit_

  def mutable_issue_comment_limit(self): self.has_issue_comment_limit_ = 1; return self.issue_comment_limit()

  def clear_issue_comment_limit(self):
    #Warning: this method does not acquire the lock.
    self.has_issue_comment_limit_ = 0;
    if self.issue_comment_limit_ is not None: self.issue_comment_limit_.Clear()

  def has_issue_comment_limit(self): return self.has_issue_comment_limit_

  def issue_attachment_limit(self):
    if self.issue_attachment_limit_ is None:
      self.lazy_init_lock_.acquire()
      try:
        if self.issue_attachment_limit_ is None: self.issue_attachment_limit_ = ActionLimit()
      finally:
        self.lazy_init_lock_.release()
    return self.issue_attachment_limit_

  def mutable_issue_attachment_limit(self): self.has_issue_attachment_limit_ = 1; return self.issue_attachment_limit()

  def clear_issue_attachment_limit(self):
    #Warning: this method does not acquire the lock.
    self.has_issue_attachment_limit_ = 0;
    if self.issue_attachment_limit_ is not None: self.issue_attachment_limit_.Clear()

  def has_issue_attachment_limit(self): return self.has_issue_attachment_limit_

  def issue_bulk_edit_limit(self):
    if self.issue_bulk_edit_limit_ is None:
      self.lazy_init_lock_.acquire()
      try:
        if self.issue_bulk_edit_limit_ is None: self.issue_bulk_edit_limit_ = ActionLimit()
      finally:
        self.lazy_init_lock_.release()
    return self.issue_bulk_edit_limit_

  def mutable_issue_bulk_edit_limit(self): self.has_issue_bulk_edit_limit_ = 1; return self.issue_bulk_edit_limit()

  def clear_issue_bulk_edit_limit(self):
    #Warning: this method does not acquire the lock.
    self.has_issue_bulk_edit_limit_ = 0;
    if self.issue_bulk_edit_limit_ is not None: self.issue_bulk_edit_limit_.Clear()

  def has_issue_bulk_edit_limit(self): return self.has_issue_bulk_edit_limit_

  def upload_limit(self):
    if self.upload_limit_ is None:
      self.lazy_init_lock_.acquire()
      try:
        if self.upload_limit_ is None: self.upload_limit_ = ActionLimit()
      finally:
        self.lazy_init_lock_.release()
    return self.upload_limit_

  def mutable_upload_limit(self): self.has_upload_limit_ = 1; return self.upload_limit()

  def clear_upload_limit(self):
    #Warning: this method does not acquire the lock.
    self.has_upload_limit_ = 0;
    if self.upload_limit_ is not None: self.upload_limit_.Clear()

  def has_upload_limit(self): return self.has_upload_limit_

  def keep_wiki_help_open(self): return self.keep_wiki_help_open_

  def set_keep_wiki_help_open(self, x):
    self.has_keep_wiki_help_open_ = 1
    self.keep_wiki_help_open_ = x

  def clear_keep_wiki_help_open(self):
    self.has_keep_wiki_help_open_ = 0
    self.keep_wiki_help_open_ = 0

  def has_keep_wiki_help_open(self): return self.has_keep_wiki_help_open_

  def keep_wiki_log_open(self): return self.keep_wiki_log_open_

  def set_keep_wiki_log_open(self, x):
    self.has_keep_wiki_log_open_ = 1
    self.keep_wiki_log_open_ = x

  def clear_keep_wiki_log_open(self):
    self.has_keep_wiki_log_open_ = 0
    self.keep_wiki_log_open_ = 0

  def has_keep_wiki_log_open(self): return self.has_keep_wiki_log_open_

  def __str__(self):
	user_str_list = []
	user_str_list.append("Username: " + str(self.get_account_username()))
	user_str_list.append("Email: " + str(self.get_account_email()))
	user_str_list.append("Number of owned projects: " + str(self.owner_of_projects_size()))
	user_str_list.append("Number of membered projects: " + str(self.member_of_projects_size()))
	return "\n".join(user_str_list)
