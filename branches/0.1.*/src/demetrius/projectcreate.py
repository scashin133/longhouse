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

"""Classes for users to create a new project.

Summary of page classes:
  ProjectCreate: Displays a simple form asking for project info,
    and handles the form submission.
"""

import sys

from common import http
from common import post
from common import validate
from common import ezt_google

import framework.helpers
import framework.constants

from demetrius import constants
from demetrius import helpers
from demetrius import permissions
from demetrius import pageclasses
from demetrius import persist


class ProjectCreate(pageclasses.DemetriusPage):
  """Shows a page with a simple form to create a project.
  """

  _PAGE_TEMPLATE = 'demetrius/project-create-page.ezt'

  def AssertBasePermission(self, req_info):
    """Assert that the user has the permissions needed to view this page."""
    pageclasses.DemetriusPage.AssertBasePermission(self, req_info)

    if not req_info.demetrius_perms.Check(permissions.CREATE_PROJECT):
      raise permissions.PermissionException(
        'You are not allowed to create a project')

  def GatherPageData(self, request, req_info):
    """Build up a dictionary of data values to use when rendering the page."""
    page_data = {
      'initialName': req_info.GetParam('proposed_project_name'),
      'initialRepositoryURL': req_info.GetParam('repositoryurl'),
      'initialSummary': req_info.GetParam('summary'),
      'initialDescription': req_info.GetParam('description'),
      'initialLicenseKey': req_info.GetParam('license_key'),
      'captcha_id' : req_info.GetParam('captcha_id'),
      'errors': req_info.errors or ezt_google.EZTError(),
      }

    page_data.update(helpers.BuildProjectAdminOptions(req_info.project,
                                                      req_info.user_pb))
    page_data.update(helpers.BuildLabelDefaults(req_info))

    post.URLCommandAttacksEncode(page_data, req_info.logged_in_user_id)
    return page_data

  def ProcessForm(self, request, req_info):
    """Process the posted form."""

    errors = ezt_google.EZTError()
    post_data = post.ParsePOSTBody(
        request, framework.constants.MAX_POST_BODY_SIZE)
    post.URLCommandAttacksCheck(post_data, req_info.logged_in_user_id)

    try:
      # Project name taken from post_data because we are creating it.
      project_name = post.LoadFieldFromPOST(
        'projectname', post_data,
        _ProjectNameValidator(self.demetrius_persist.IsValidProjectName))
    except validate.InvalidFormattedField, e:
      errors.projectname = e.text
      project_name = post.LoadFieldFromPOST('projectname', post_data)

    try:
      repositoryurl = post.LoadFieldFromPOST('repositoryurl', post_data)
    except validate.InvalidFormattedField, e:
      #errors.repositoryurl = e.text
      #repositoryurl = post.LoadFieldFromPOST('repositoryurl', post_data)
      repositoryurl = ''

    try:
      summary = post.LoadFieldFromPOST('summary', post_data,
                                       validator=validate.Required())
    except validate.InvalidFormattedField, e:
      errors.summary = e.text
      summary = post.LoadFieldFromPOST('summary', post_data)

    try:
      description = post.LoadFieldFromPOST('description', post_data,
                                           validator=validate.Required())
    except validate.InvalidFormattedField, e:
      errors.description = e.text
      description = post.LoadFieldFromPOST('description', post_data)

    try:
      license_key = post.LoadFieldFromPOST('license_key', post_data,
                                           validator=validate.Required())
    except validate.InvalidFormattedField, e:
      errors.licensekey = e.text
      license_key = post.LoadFieldFromPOST('license_key', post_data)

    labels = []
    if 'label' in post_data: labels = post_data['label']  # a list
    labels = [post.CanonicalizeLabel(label) for label in labels]

    restricted_labels = helpers.FilterRestrictedLabels(req_info, labels)
    if restricted_labels:
      errors.labels = 'You may not use: %s' % ', '.join(restricted_labels)

    # These are not specified on via the ProjectCreate form,
    # the user must edit the project after creation to set them.
    member_ids = []
    links = []

    if not errors.AnyErrors():
      try:
        self.demetrius_persist.CreateProject(
          project_name, [req_info.logged_in_user_id], member_ids, summary,
          repositoryurl, description, labels, license_key, self.conn_pool,
          worktable=self.worktable)
      except persist.ProjectAlreadyExists, e:
        errors.projectname = 'That project name is not available.' # TODO: i18n

    if errors.AnyErrors():
      req_info.PrepareForSubrequest(
        None, errors, summary=summary, repositoryurl=repositoryurl,
        description=description, license_key=license_key,
        labels=labels, proposed_project_name=project_name)
      self.Handler(request, req_info=req_info)
      return

    # Go to the new project's summary page.
    url = framework.helpers.FormatAbsoluteURL(
      None, constants.SUMMARY_PAGE_URL, request,
      project_name=project_name)
    http.SendRedirect(url, request)


class _ProjectNameValidator(object):
  """Validator class for project names."""

  def __init__(self, validator):
    """Set up the validator.

    Args:
      validator: Validation method that takes a project name string
        and returns its validity as a boolean value.
    """
    self.validator = validator

  def Validate(self, projectname):
    """Validate a project name using a regular expression.

    Args:
      projectname: The name of a project as a string.

    Raises:
      AssertionError: The name provided project name is not valid.
    """
    if not self.validator(projectname[0]):
      self.Fail('Invalid project name')

  def Fail(self, message):
	raise validate.InvalidFormattedField(message)


if __name__ == '__main__':
  sys.exit('This is not meant to be run as a standalone program. Exiting.')
