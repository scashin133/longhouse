import os

import generated_demetrius_pb
from framework import constants
from framework.svncontrols import SvnController, SvnException


class Project_LinksURL(generated_demetrius_pb.Project_LinksURL):
    def __init__(self):
        generated_demetrius_pb.Project_LinksURL.__init__(self)
        
class Project_LinksBlog(generated_demetrius_pb.Project_LinksBlog):
    def __init__(self):
        generated_demetrius_pb.Project_LinksBlog.__init__(self)
        
class Project_LinksGroup(generated_demetrius_pb.Project_LinksGroup):
    def __init__(self):
        generated_demetrius_pb.Project_LinksGroup.__init__(self)
        
class Project_LinksIssues(generated_demetrius_pb.Project_LinksIssues):
    def __init__(self):
        generated_demetrius_pb.Project_LinksIssues.__init__(self)


class Project(generated_demetrius_pb.Project):
    def __init__(self):
        generated_demetrius_pb.Project.__init__(self)
        self.svn_controller_ = ''
    
    # svn controller stuff is too complex to be handled
    # by the yaml files so it goes here
    
    def setup_svn_controller(self):
        print 'setting up svn controller for project', self.project_name()
        
        try:
            working_copy_root = os.path.join(
                constants.WORKING_DIR, 
                constants.VERSIONED_STORAGE_ROOT,
                self.project_name())
            
            repository_location = self.persist_repository_url()
            repository_username = self.persist_repository_username()
            repository_password = self.persist_repository_password()
            
            self.svn_controller_ = SvnController(
                     repository_location,
                     repository_username,
                     repository_password,
                     working_copy_root)
            print 'Connected to svn repository:', repository_location
            
            
            if(self.svn_controller().has_working_copy()):
                print 'already have working copy, updating'
                self.svn_controller().d_up()
            else:
                print 'checking out', self.svn_controller().repository_location
                self.svn_controller().d_checkout()
            
        except SvnException:
            print 'Failed to connect to svn repository'
            self.svn_controller_ = ''
            raise
        
    def svn_controller(self):
        return self.svn_controller_
    
    def has_svn_controller(self):
        return (self.svn_controller_ != '')
    
    def has_working_copy(self):
        if (self.has_svn_controller() and self.svn_controller().has_working_copy()):
            print 'has working copy?', self.svn_controller().has_working_copy()
            return self.svn_controller().has_working_copy()
        else:
            print 'does not have working copy'
            return False
        
class User(generated_demetrius_pb.User):
    def __init__(self):
        generated_demetrius_pb.User.__init__(self)
        
    def verify_account_password(self, p):
        if self.account_password() == p:
          return True
        else:
          return False
