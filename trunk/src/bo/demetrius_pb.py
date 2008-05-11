import os

import generated_demetrius_pb
from framework import constants
from framework.svncontrols import SvnController, SvnException

import twisted.internet.threads
import twisted.internet.utils
from twisted.internet import reactor, defer

from framework import constants

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
    
    def d_setup_svn_controller(self):
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
        
            d = self.svn_controller().d_test()
            
            def test_result(result):
                if result == False:
                    self.svn_controller_ = ''
                    raise Exception('problem setting up svn controller, self test failed')
                else:
                    return self.d_checkout_working_copy()
            
            d.addCallback(test_result)
            
            return d
        
        except Exception, e:
            print 'exception in d_setup_svn_controller', e
            raise
        
    def d_checkout_working_copy(self):
        if(self.svn_controller().has_working_copy()):
            print 'already have working copy, updating'
            return self.svn_controller().d_up()
        else:
            print 'checking out', self.svn_controller().repository_location
            return self.svn_controller().d_checkout()
        
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
