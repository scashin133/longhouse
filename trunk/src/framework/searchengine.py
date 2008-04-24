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

"""A set of functions that integrate a search engine with Demetrius.
"""

import re
import os
import types


BOOL = 'BOOL'
NUM = 'NUM'
TXT = 'TXT'


class SEField:
  """Represents a field in a structured search engine document. E.g., summary.
  """

  def __init__(self, label, type):
    """Initialize the field label and type.

    Args:
      label: the name of the field that the user will use.
      type: BOOL, NUM, or TXT.
    """
    self.key = label.lower()
    self.label = self.key
    self.type = type


class SearchEngine(object):
  """This class provides an interface between demetrius and a search engine.

  This class does the following things:
    + converts user queries to search engine query syntax
    + runs queries and returns a list of docids or result URLs
    + passes documents to the indexer process.
  """

  def __init__(self):
    """Initialize this module so that it is ready to use."""
    # TODO(students): set up pylucene or whatever

  def _ParseUserQuery(self, query, scope, project_name, doctype, fields):
    """Parse a user query and return an equivelant search engine query.

    Args:
      query: string with user's query.
      scope: search terms, added by IssueIndex or ProjectIndex, that define
             the scope of the query in the user query language.  E.g.,
             adding the canned query.
      project_name: string name of the project to search; if None,
             search all projects.
      doctype: adds an additional search term that limits results
               to only those documents of the desired type.  I.e., only
               issues or only project descriptions.
      fields: {field_name: SEField(field_name, type), ...}
              a dictionary mapping field names to SEField objects.

    Returns: a string with the appropriate search engine query.
    """
    # TODO(students): parse the user query into format used by search engine.
    return ''


  def _SendQuery(self, engine_query, req_info, start=0, num=3000,
                 return_urls=False):
    """Run a search engine query and return the matching docids or URLs.

    Args:
      engine_query: search query in search engine syntax.
      req_info: commonly used info parsed from the request.
      start: index of first result to return. We skip 0..start-1.
      num: max number of results to return.
      return_urls: True to return document URLs instead of docids.

    Results: a list of docids that satisfy the query, or
    a list of urls if return_urls was True.
    """
    # TODO(students): send a query to the search engine and return the results.
    return []

  ### Functions to update the search engine index.

  def _WriteDocument(self, key, document_pb):
    """Tell the search engine to index the given document

    Args:
      key: the docid for this document.
      document_pb: document PB to store.
    """
    # TODO(students): put the document into the search engine.
    pass

  def _MarkupUnstructured(self, labels, doctype, **sections):
    """Return as string with begin_ and end_ markers around each section.

    Args:
      labels: a list of strings for used-defined labels.
      doctype: adds search engine document tokens that limit results
               to only those documents of the desired type.
      **sections: each keyword argument is considered to be a section with
                  the name of the keyword argument used as the name of the
                  section.  Section values may be anything that converts
                  to a string.

    Returns: a string with all sections and section begin_ and end_ markers.
    """

    parts = ['begin_documenttype %s end_documenttype' % doctype]

    for lab in labels:
      if '-' in lab:
        key, val = lab.split('-', 1)
        parts.append('begin_u_%s %s end_u_%s' % (key, val, key))

    parts.append('begin_label %s end_label' % ' '.join(labels))

    for section_name, section_value in sections.items():
      parts.append('begin_' + section_name)
      if type(section_value) == types.ListType:
        parts.extend(map(_Str22Format, section_value))
      else:
        parts.append(_Str22Format(section_value))
      parts.append('end_' + section_name)

    return '\n'.join(parts)


def _Str22Format(value):
  """Convert value to String in ptyhon2.2 format for backward compatability."""
  if value == True:
    return '1'
  elif value == False:
    return '0'
  else:
    return str(value)
