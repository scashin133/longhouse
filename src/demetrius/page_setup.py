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

"""This file sets up the urls for Demetrius pages.
"""

import sys

from twisted.python import log

from common import pageclasses

import framework.constants
import framework.helpers

from demetrius import constants
from demetrius import login
from demetrius import logout
from demetrius import hostinghome
from demetrius import projectadminportal
from demetrius import projectadmin
from demetrius import projectsource
from demetrius import projectfeeds
from demetrius import projectsummary
from demetrius import projectpeople
from demetrius import projectcreate
from demetrius import user_profile
from demetrius import user_settings
from demetrius import user_registration
from demetrius import user_validation
from demetrius import placeholderpage


# The location where we keep our templates, images, css, etc.
_DATA_DIR = 'htdocs'

class PageSetup(framework.helpers.AbstractPageSetup):
  """This class configures the Demetrius URLs."""

  def __init__(self, server, conn_pool,
               demetrius_persist, dit_persist,
               worktable, universal_ezt_data):
    self.server = server
    self.conn_pool = conn_pool
    self.demetrius_persist = demetrius_persist
    self.dit_persist = dit_persist
    self.worktable = worktable
    self.universal_ezt_data = universal_ezt_data.copy()

  def RegisterPages(self):
    """Register all the Demetrius pages, forms, and feeds with the server."""
    self._RegisterProjectHandlers()
    self._RegisterSiteHandlers()
    self._RegisterStaticFiles()
    self._RegisterRedirects()
    log.msg('Finished registering Demetrius handlers.')

  def _RegisterProjectHandlers(self):
    """Register page and form handlers that operate within a project."""

    summary_page = projectsummary.ProjectSummary(
      self.conn_pool, self.demetrius_persist, 
      self.dit_persist, self.universal_ezt_data)
    self._SetupProjectPage(summary_page.Handler,
                           constants.SUMMARY_PAGE_URL)

    people_page = projectpeople.ProjectPeople(
      self.conn_pool, self.demetrius_persist, 
      self.dit_persist, self.universal_ezt_data)
    self._SetupProjectPage(people_page.Handler,
                           constants.PEOPLE_PAGE_URL)
    
    admin_portal_page = projectadminportal.ProjectAdminPortal(
      self.conn_pool, self.demetrius_persist, self.universal_ezt_data)
    self._SetupProjectPage(admin_portal_page.Handler,
                           constants.ADMIN_PORTAL_PAGE_URL)

    admin_meta_page = projectadmin.ProjectAdmin(
      self.conn_pool, self.demetrius_persist, self.universal_ezt_data)
    self._SetupProjectPage(admin_meta_page.Handler,
                           constants.ADMIN_META_PAGE_URL)
    self._SetupProjectForm(admin_meta_page.FormHandler,
                           constants.ADMIN_META_FORM_URL)
    
    admin_persist_page = projectadmin.ProjectAdminPersist(
      self.conn_pool, self.demetrius_persist, self.universal_ezt_data)
    self._SetupProjectPage(admin_persist_page.Handler,
                           constants.ADMIN_PERSIST_PAGE_URL)
    self._SetupProjectForm(admin_persist_page.FormHandler,
                           constants.ADMIN_PERSIST_FORM_URL)
                           
    # unfinished handler to generate a helper file for the post-commit hook
    #self._SetupProjectPage(admin_persist_page.HookFileHandler, '/myproject.longhouse')
                           
                           


    admin_members_page = projectadmin.ProjectAdminMembers(
      self.conn_pool, self.demetrius_persist, self.universal_ezt_data)
    self._SetupProjectPage(admin_members_page.Handler,
                           constants.ADMIN_MEMBERS_PAGE_URL)
    self._SetupProjectForm(admin_members_page.FormHandler,
                           constants.ADMIN_MEMBERS_FORM_URL)

    project_members_feed = projectfeeds.ProjectMembersFeed(
      self.conn_pool, self.demetrius_persist, self.universal_ezt_data)
    self._SetupProjectPage(project_members_feed.Handler,
                           constants.PROJECT_MEMBERS_FEED_URL)

    admin_advanced_page = projectadmin.ProjectAdminAdvanced(
      self.conn_pool, self.demetrius_persist, self.universal_ezt_data)
    self._SetupProjectPage(admin_advanced_page.Handler,
                           constants.ADMIN_ADVANCED_PAGE_URL)
    self._SetupProjectForm(admin_advanced_page.FormHandler,
                           constants.ADMIN_ADVANCED_FORM_URL)
    
    source_page = projectsource.ProjectSource(
      self.conn_pool, self.demetrius_persist, self.universal_ezt_data)
    self._SetupProjectPage(source_page.Handler,
                           constants.SOURCE_PAGE_URL)
    
    
    
    #PLACEHOLDER PAGES#
    #Replace these with real pages once the pages are built#
    
    placeholder_page = placeholderpage.PlaceholderPage(
      self.conn_pool, self.demetrius_persist, self.universal_ezt_data)
    self._SetupProjectPage(placeholder_page.Handler,
                           constants.DOWNLOADS_INDEX_URL)
    self._SetupProjectPage(placeholder_page.Handler,
                           constants.WIKI_INDEX_URL)
    self._SetupProjectPage(placeholder_page.Handler,
                           constants.ADMIN_DOWNLOADS_PAGE_URL)
    self._SetupProjectPage(placeholder_page.Handler,
                           constants.ADMIN_WIKI_PAGE_URL)
    
    # TODO: register per project deferred pages here

  def _RegisterSiteHandlers(self):
    """Register page and form handlers that aren't associated with projects."""
    
    user_profile_page = user_profile.UserProfile(
      self.conn_pool, self.demetrius_persist, self.universal_ezt_data)
    self._SetupUserPage(user_profile_page.Handler,
                           constants.USER_PROFILE_PAGE_URL)
    
    user_settings_page = user_settings.UserSettings(
      self.conn_pool, self.demetrius_persist, self.universal_ezt_data)
    self._SetupSitePage(user_settings_page.Handler,
                        constants.USER_SETTINGS_PAGE_URL)
    
    user_registration_page = user_registration.UserRegistration(
      self.conn_pool, self.demetrius_persist, self.universal_ezt_data)
    self._SetupSitePage(user_registration_page.Handler,
                        constants.REGISTRATION_PAGE_URL)
    self._SetupSiteForm(user_registration_page.FormHandler,
                        constants.REGISTRATION_FORM_URL)
    
    user_validation_page = user_validation.UserValidation(
      self.conn_pool, self.demetrius_persist, self.universal_ezt_data)
    self._SetupSitePage(user_validation_page.Handler,
                        constants.VALIDATION_PAGE_URL)
    self._SetupSiteForm(user_validation_page.FormHandler,
                        constants.VALIDATION_FORM_URL)


    login_page = login.LoginPage(
      self.conn_pool, self.demetrius_persist, self.universal_ezt_data)
    self._SetupSitePage(login_page.Handler,
                           constants.LOGIN_PAGE_URL)
    self._SetupSiteForm(login_page.FormHandler,
                           constants.LOGIN_FORM_URL)

    logout_page = logout.LogoutPage(
      self.conn_pool, self.demetrius_persist, self.universal_ezt_data)
    self._SetupSiteForm(logout_page.FormHandler,
                        constants.LOGOUT_PAGE_URL)

    create_page = projectcreate.ProjectCreate(
      self.conn_pool, self.demetrius_persist, self.universal_ezt_data,
      worktable=self.worktable)
    self._SetupSitePage(create_page.Handler,
                        constants.PROJECT_CREATE_PAGE_URL)
    self._SetupSiteForm(create_page.FormHandler,
                        constants.PROJECT_CREATE_FORM_URL)

    hosting_home = hostinghome.HostingHome(
      self.conn_pool, self.demetrius_persist, self.universal_ezt_data)
    self.server.RegisterHandler(constants.HOSTING_HOME_URL,
                                hosting_home.Handler)  
    
                                
    # PLACEHOLDER PAGES
    # Replace these with real pages once the pages are built
    
    placeholder_page = placeholderpage.PlaceholderPage(
      self.conn_pool, self.demetrius_persist, self.universal_ezt_data)
    self._SetupSitePage(placeholder_page.Handler,
                           constants.SEARCH_PAGE_URL)

  def _RegisterRedirects(self):
    """Register redirects among pages inside demetrius."""
    redirect = pageclasses.Redirect(constants.HOSTING_HOME_URL)
    self.server.RegisterHandler('/p', redirect.Handler)
    self.server.RegisterHandler('/p/', redirect.Handler)
    # Only keep this if the web site has no other HTML home page.

  def _RegisterStaticFiles(self):
    """Register static page for CSS and JS files used in demetrius."""
    self.server.RegisterStaticFiles('css', 'htdocs/css')
    self.server.RegisterStaticFiles('images', 'htdocs/images')
    self.server.RegisterStaticFiles('js', 'htdocs/js')
    self.server.RegisterStaticFiles('files', 'htdocs/files')



if __name__ == '__main__':
  sys.exit('This is not meant to be run as a standalone program. Exiting.')
