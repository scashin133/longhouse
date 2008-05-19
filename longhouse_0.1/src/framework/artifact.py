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

"""Helper functions for displaying individual project artifacts and comments.
"""

import time

from ezt import ezt

from common import post
from common import ezt_google
from common import timestr

from bo import artifact_pb
from demetrius import permissions

#from bo import worktable_pb


def LoadCommentFromPost(post_data, req_info, artifact, errors):
  """Return an ArtifactComment PB based on info entered by the user."""
  ac = artifact_pb.ArtifactComment()
  ac.set_creator_user_id(req_info.logged_in_user_id)
  ac.set_mod_time(int(time.time()))
  if 'content' in post_data:
    ac.set_content(post_data['content'][0])

  if 'summary' in post_data:
    new_summary = post_data['summary'][0]
    if new_summary != artifact.summary():
      update_pb = artifact_pb.ArtifactComment_Updates()
      update_pb.set_field(artifact_pb.ArtifactComment_Updates.SUMMARY)
      update_pb.set_newvalue(new_summary)
      ac.updates_list().append(update_pb)

  # FUTURE: refactor handling of Owner, CC, and Status updates to here.

  if 'label' in post_data:
    labels = post_data['label']
    labels = [post.CanonicalizeLabel(lab) for lab in labels
              if lab.strip()]  # skip blanks

    # compute the set of labels added and removed
    labels_added = [lab for lab in labels
                    if lab not in artifact.labels_list()]
    labels_removed = [lab for lab in artifact.labels_list()
                      if lab not in labels]
    if labels_added or labels_removed:
      update_str = ' '.join(['-%s' % lab for lab in labels_removed]
                            + labels_added)
      update_pb = artifact_pb.ArtifactComment_Updates()
      update_pb.set_field(artifact_pb.ArtifactComment_Updates.LABELS)
      update_pb.set_newvalue(update_str)
      ac.updates_list().append(update_pb)

  return ac


class ArtifactCommentPBProxy(ezt_google.PBProxy):
  """Wrapper class to easily display an ArtifactComment in EZT."""

  def __init__(self, comment_pb, user_proxy,
               logged_in_user_id, perms, wrap=True,
               wiki_objs=None):
    """Get ArtifactComment PB and make its fields available as attrs.

    Args:
      comment_pb: ArtifactComment business object.
      user_proxy: UserIDProxy for the user that entered the comment.
      logged_in_user_id: user id of current user, or None.
      perms: Tool-specific permissions object for logged in user, or None.
      wrap: True if the comment should be word-wrapped.
      wiki_objs: tuple of a bunch of objects needed to render a
        comment in wiki format.
    """
    ezt_google.PBProxy.__init__(self, comment_pb)

    self.creator = user_proxy
    time_tuple = time.localtime(comment_pb.mod_time())
    self.date_string = timestr.ComputeAbsoluteDate(comment_pb.mod_time())
    self.date_relative = timestr.ComputeRelativeDate(comment_pb.mod_time())
    self.date_tooltip = time.asctime(time_tuple)
    # TODO: make sure that dates and times are localized
    self.content = MarkupCommentOnOutput(comment_pb.content(), wrap, wiki_objs)
    self.update_objs = [ArtifactUpdateProxy(update_pb)
                        for update_pb in comment_pb.updates_list()]
    self.sequence = comment_pb.sequence # BT timestamp order of comments
    self.is_deleted = comment_pb.has_deleted_by()
    self.can_delete = permissions.CanDelete(logged_in_user_id, perms,
                                            comment_pb)
    self.visible = self.can_delete or not comment_pb.has_deleted_by()


def MarkupCommentOnOutput(content, wrap, wiki_objects):
  """Prepare the comment for display."""
  # Case 1: wiki comments
  if wiki_objects:
    (project, parser, formatter, renderer, dwiki_persist,
     dit_persist) = wiki_objects
    parsed_page = parser.Parse(content)
    compiled_page, _ = formatter.Format(
      project.project_name(), parsed_page, dwiki_persist)
    content = renderer.Render(
      project, compiled_page, True, dit_persist)

  # Case 2: plain text comments that should be word-wrapped.
  elif wrap:
    content = post.FormPlainTextToSafeHtml(content)

  # Case 3: verbatim comments that are output in <pre> tags.
  else:
    content = post.SafeForHTML(content)

  return content


class LabelProxy(object):
  """Wrapper class that makes it easier to display a label via EZT."""

  def __init__(self, label):
    """Make several values related to this label available as attrs.

    Args:
      label: artifact label string.  E.g., 'Priority-High' or 'Frontend'.
    """

    self.name = label

    _LABEL_DISPLAY_CHARS = 30
    _LABEL_PART_DISPLAY_CHARS = 15
    self.docstring = ''
    self.short_name, self.tooltip = ezt_google.FitString(
      label, _LABEL_DISPLAY_CHARS)
    if '-' in label:
      self.prefix, self.value = label.split('-', 1)
      self.short_prefix, _ = ezt_google.FitString(
        self.prefix, _LABEL_PART_DISPLAY_CHARS)
      self.short_value, _ = ezt_google.FitString(
        self.value, _LABEL_PART_DISPLAY_CHARS)
    else:
      self.prefix, self.short_prefix = '', ''
      self.value, self.short_value = label, self.short_name


class ArtifactUpdateProxy(object):
  """Wrapper class to easily display an ArtifactComment Update in EZT."""

  def __init__(self, update_pb):
    """Get the info from the PB and put it into easily accessible attrs.

    Args:
      update_pb: Update part of an ArtifactComment business object.
    """
    self.newvalue = update_pb.newvalue()
    field_id = update_pb.field()
    field_name = artifact_pb.ArtifactComment_Updates._FIELD_ID_NAMES[field_id]
    self.field_name = field_name.capitalize()


def BuildCommentSettings(config):
  """Return EZT data used by artifact-comment-admin.ezt."""
  return {
    'allow_comments': ezt.boolean(config.allow_comments()),
    'comment_notify': config.comment_notify_address(),
    }


def ParseCommentSettings(post_data):
  """Parse the project's visitor comments settings out of an HTML form.

  Assumes that the form included artifact-comment-admin-part.ezt.
  """
  allow_comments = 'allow_comments' in post_data

  comment_notify_address = ''
  if 'comment_notify' in post_data:
    comment_notify_address = post_data['comment_notify'][0]

  return (allow_comments, comment_notify_address,)


def SendArtifactCommentNotificaton(
  project_name, artifact_name, artifact_type, comment_id,
  detail_url, change_description, omit_user_ids, creator_user_id, worktable):
  """Create and store an ArtifactCommentNotification work item."""
  acn = worktable_pb.ArtifactCommentNotification()
  acn.set_project_name(project_name)
  acn.set_artifact_name(artifact_name)
  acn.set_artifact_type(artifact_type)
  acn.set_comment_id(comment_id)
  acn.set_detail_url(detail_url)
  acn.set_change_description(change_description)
  acn.set_creator_user_id(creator_user_id)
  acn.omit_user_ids_list().extend(omit_user_ids)

  worktable.AddItem('artifact-comment', acn)
