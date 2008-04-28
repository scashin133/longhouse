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

"""A set of functions that integrate a search engine with the Demetrius Issue Tracker.

This module implements functions to search and to update
the search engine's respository after any DIT issue is changed.
"""

import re

from twisted.python import log

#from bo import dit_ms_pb

from framework import searchengine


# Predefined issue fields
ISSUE_FIELDS = {
  'cc': searchengine.SEField('Cc', searchengine.TXT),
  'comment': searchengine.SEField('Comment', searchengine.TXT),
  'commentby': searchengine.SEField('CommentBy', searchengine.TXT),
  'description': searchengine.SEField('Description', searchengine.TXT),
  'label': searchengine.SEField('Label', searchengine.TXT),
  'open': searchengine.SEField('Open', searchengine.BOOL),
  'owner': searchengine.SEField('Owner', searchengine.TXT),
  'project': searchengine.SEField('Project', searchengine.TXT),
  'reporter': searchengine.SEField('Reporter', searchengine.TXT),
  'stars': searchengine.SEField('Stars', searchengine.NUM),
  'starredby': searchengine.SEField('StarredBy', searchengine.TXT),
  'status': searchengine.SEField('Status', searchengine.TXT),
  'summary': searchengine.SEField('Summary', searchengine.TXT),
  }


# We use this to keep issues separate from project descriptions.
ISSUE_TYPE = 'issue'


# Users can use "me" in queries to refer to the logged in user name.
# Since non-gmail users can star issues, we must use user ids.
IS_STARRED_RE = re.compile(r'\bis:starred\b')

# Users can use "me" in other fields to refer to the logged in user name.
ME_RE = re.compile(r'\bme\b')


class IssueIndex(searchengine.SearchEngine):
  """This class handles issue search and issue index building requests.

  IssueIndex uses the SearchEngine class to parse and run issue queries and to
  submit revised search engine documents to the search engine. Also, it adds
  DIT-specific fields and additional user query syntax.
  """

  ### Functions to search

  def SearchProjectCan(self, user_query, project_name, canned_query,
                       logged_in_user_proxy, req_info):
    """Run the user's query in the context of a project's canned query.

    Args:
      user_query: string of user query in user syntax.
      project_name: the name of the project to search in.
      canned_query: string of canned query context in user syntax.
      logged_in_user_proxy: Null when no user is logged in, otherwise
        a UserIDProxy for the logged in user.
      req_info: commonly used info parsed from the request.

    Returns: a list of issue ids within the project that satisfy the query.
    """
    scope = canned_query
    query = user_query
    if logged_in_user_proxy:
      query = IS_STARRED_RE.sub(
        'starredby:%016x' % logged_in_user_proxy.user_id, query)
      query = ME_RE.sub(logged_in_user_proxy.username, query)
      scope = IS_STARRED_RE.sub(
        'starredby:%016x' % logged_in_user_proxy.user_id, scope)
      scope = ME_RE.sub(logged_in_user_proxy.username, scope)
    else:
      query = IS_STARRED_RE.sub('', query)
      query = ME_RE.sub('', query)
      scope = IS_STARRED_RE.sub('', scope)
      scope = ME_RE.sub('', scope)

    ms_query = self._ParseUserQuery(query, scope, project_name,
                                    ISSUE_TYPE, ISSUE_FIELDS)

    docids = self._SendQuery(ms_query, req_info)
    issue_ids = [self._GetIssueIdFromDocid(docid) for docid in docids]
    return issue_ids

  ### Functions to update the search engine repositiory

  def WriteIssue(self, project_pb, issue_id, summary, owner_name,
                 reporter_name, cc_names, starrer_ids,
                 status_name, means_open,
                 label_names, description, commentor_names,
                 comment_contents):
    """Write all details of an issue to the search engine.

    Each detail is represented twice: once as structured attributes, and once
    as unstructured text.

    Args:
      project_pb: the business object for the project containing the issue.
      issue_id: the issue if of the issue to index.
      means_open: True if this issue is an open issue, False if closed.
      all other fields are strings or lists of strings with content from the
      issue.
    """

    issue_document_pb = dit_ms_pb.IssueDocument()
    self._SetUnstructured(issue_document_pb, project_pb.project_name(),
                          summary, owner_name, reporter_name, cc_names,
                          starrer_ids, status_name, means_open,
                          label_names, description, commentor_names,
                          comment_contents)

    issue_url = '/p/%s/issues/detail?id=%d' % (
      project_pb.project_name(), issue_id)
    issue_document_pb.set_url(issue_url)

    key = None  # TODO: reimplement choice of docid.
    self._WriteDocument(key, issue_document_pb)


  def _SetUnstructured(self, document_pb, project_name, summary,
                       owner_name, reporter_name, cc_names,
                       starrer_ids, status_name, means_open, label_names,
                       description, commentor_names, comment_contents):
    """Combine all textual parts of an issue into one unstructured document.

    Args:
      document_pb: seaerch engine document object.
      means_open: True if this issue is an open issue, False if closed.
      all other fields are strings or lists of strings with content from the
      issue.

    We are marking up the unstructured text with delimiter tokens so that
    we can use regular search engine operators to search for text in specific
    fields.
    """

    # Note: the keyword arg names do not follow our coding standard
    # because they are used as the search keywords that the user enters.
    markup = self._MarkupUnstructured(
      label_names, ISSUE_TYPE,
      project=project_name, summary=summary, owner=owner_name,
      reporter=reporter_name, stars=str(len(starrer_ids)),
      starredby=' '.join(['%016x' % user_id for user_id in starrer_ids]),
      status=status_name, open=means_open,
      description=description, cc=cc_names,
      commentby=commentor_names, comment=comment_contents)

    log.msg('_SetUnstructured %s' % markup)
    document_pb.set_text(markup)
