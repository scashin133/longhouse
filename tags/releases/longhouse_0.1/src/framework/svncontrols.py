import commands
import shutil
import os
from time import strftime
import re
import glob
import string
import commands

import twisted.internet.utils
from twisted.internet import reactor, defer

from framework import constants

def deferred_helloworld(self):
    d = defer.Deferred()
    reactor.callLater(2, d.callback, 'hello, world!')
    return d

class ProjectSvnUpPage:
    
    def __init__(self, demetrius_persist):
        self.demetrius_persist = demetrius_persist
    
    def Handler(self, request):
        
        self.request = request
        
        self.project_name = request.path.split('/')[2]
        project = self.demetrius_persist.GetProject(self.project_name)
        
        if project is None:
            return self.return_err_msg('project not found')
        
        try:
            d = self.demetrius_persist.GetProject(self.project_name).svn_controller().d_up()
            d.addCallback(self.load_fresh_xml)
            d.addErrback(self.return_err_msg)
            d.addCallback(self.return_msg)
            d.addErrback(self.return_err_msg)
            return d
        except Exception, e:
            return self.return_err_msg(e)

    def load_fresh_xml(self, *args):
        self.demetrius_persist.GetProject(self.project_name, fresh=True)

    def return_err_msg(self, e):
        self.request.write('Error: ' + str(e))

    def return_msg(self, *args):
         self.request.write('Done.')
    

class SvnController:
    
    SUCCESS = 0
    ERROR = 256
    
    CONFLICT_FILES = re.compile('^C\s+(.*)$', re.MULTILINE)
    
    def __init__(self, repository_location, 
                 repository_username,
                 repository_password,
                 working_copy_root=""):
        """
        Initialize a new SvnController. Repository location must be specified.
        You may also optionaly specify a location to check out
        working copies to.
        """
        
        self.repository_location = repository_location
        self.repository_username = repository_username
        self.repository_password = repository_password
        
        # if the repository location does not already end in a slash, add one
        if self.repository_location[len(self.repository_location)-1:] != "/":
            self.repository_location += "/"
        
        self.working_copy_root = working_copy_root
        
        # likewise, if the working copy root is not blank and
        # does not end in a slash, add one
        if (len(self.working_copy_root) > 0) and\
            (self.working_copy_root[len(self.working_copy_root)-1:] != "/"):
            self.working_copy_root += "/"
        
    def d_test(self): 
        """Determine if we can contact the repository."""
        d = self.d_remote_list('/')
        d.addCallback(self._return_success)
        return d
    
    def _return_success(self, output):
        if output[2] == self.SUCCESS:
            return True
        else:
            return False
        
    def _print_response(self, response):
        print 'got response:', response
        return response
        
    def _print_error(self, error):
        print 'error in deferred:', error
    
    def _print_timeout(self, error):
        print 'timeout in deferred'
    
    def is_working_copy(self, path):
        """
        Check if the given path is a working copy 
        (contains a .svn directory)
        """
        if (len(path) > 0) and (path[len(path)-1:] != '/'):
            path += '/'
        # TODO: would this work? return os.path.exists(os.path.join(path, '.svn'))
        return os.path.exists(path + ".svn")
    
    def has_working_copy(self):
        """
        check if working_copy_root is a working copy
        """
        print 'checking if', self.working_copy_root, 'is working copy'
        return self.is_working_copy(self.working_copy_root)
    
    def d_remote_list(self, dir, ):
        """
        Perform a 'svn list' command on the repository
        """
        args = ['list', 
                url_join(self.repository_location, dir),
                '--username', self.repository_username, 
                '--password', self.repository_password]
        
        return twisted.internet.utils.getProcessOutputAndValue(
                    constants.SVN_LOC, args)


    def d_checkout(self, repo_dir = '', local_path = '#'):
        """
        Checkout a working copy. If repo_dir is not specified, check out
        the root of the repository. If local_path is not specified, 
        use the previously given working copy root
        TODO: untested
        """
            
        if local_path == '#':
            local_path = self.working_copy_root
        
        args = ['co', 
                url_join(self.repository_location, repo_dir),
                local_path,
                '--username', self.repository_username, 
                '--password', self.repository_password]
        
        return twisted.internet.utils.getProcessOutputAndValue(
                    constants.SVN_LOC, args)


    def d_up_add_commit(self, message="generic Longhouse commit"):
        
        def print_result(result):
            print '\treturned:', result
            
        self.message = message
        d = self._d_cleanup()
        d.addCallback(self.d_up)
        d.addCallback(self._d_add_all)
        d.addCallback(print_result)
        d.addCallback(self._d_commit)
        d.addCallback(print_result)
        


    def d_up(self, *args):
        """
        Perform a 'svn up' opperation. By default the 
        path is the working copy root. Handle any bad merges by
        having local changes take priority. 
        """
        
        args = ['up', self.working_copy_root]
        
        d = twisted.internet.utils.getProcessOutputAndValue(
                    constants.SVN_LOC, args)
        d.addCallback(self._handle_bad_merges)
        
        return d
    
    
    def _d_cleanup(self, *args):
        
        args = ['cleanup']
        
        return twisted.internet.utils.getProcessOutputAndValue(
                    constants.SVN_LOC, args)
    

    def _d_add_all(self, *args):
        """
        Add the specified file or directory to the repository. It
        will be checked in in the next commit.
        """

        d = defer.Deferred()

        # recursively walk directories, adding everything we find to svn
        for root, dirs, files in os.walk(self.working_copy_root):
            
            # remove any hidden dirs
            for dir in dirs:
                if dir.startswith("."):
                    dirs.remove(dir)
            
            for dir in dirs:
                print dir, os.path.join(root, dir)
                args = ['add', os.path.join(root, dir)]
                d.addCallback(ProcessOutputFactory(constants.SVN_LOC, args))
            
            for name in files:
                print name, os.path.join(root, name)
                args = ['add', os.path.join(root, name)]
                d.addCallback(ProcessOutputFactory(constants.SVN_LOC, args))
        
        # start the chain of deferreds
        d.callback('empty')
        
        return d 


    def _d_commit(self, *args):
        """
        Perform a 'svn commit' command. If no directory is specified, 
        commit the working copy root.
        """
            
        if self.message == None:
            self.message = 'generic Longhouse commit'
        
        args = ['ci', 
                self.working_copy_root, 
                '--username', self.repository_username, 
                '--password', self.repository_password,
                '-m', '"%s"' % self.message]
        
        d = twisted.internet.utils.getProcessOutputAndValue(constants.SVN_LOC, args)
        self.message = None
        return d

    def _handle_bad_merges(self, output):
        """
        resolve any bad merges by replacing them with
        the pre-merge file, then removing the .mine file
        and two .r# files
        TODO: this might not be twisted thread safe, if shutil.copyfile
        or os.remove takes too long we might get an interrupted system call error
        """
            
        bad_merges = self.CONFLICT_FILES.findall(output[0])
        
        for bad_merge in bad_merges:
            print 'correcting bad merge on file', bad_merge
            
            # use the .mine file as resolution (local changes take priority)
            shutil.copyfile(bad_merge + '.mine', bad_merge)
            
            # remove the .mine file and both .r* files
            os.remove(bad_merge + '.mine')
            for revision_file in glob.glob(bad_merge + '.r*'):
                os.remove(revision_file)

def ProcessOutputFactory(process, args):
    """ Returns a callable that will execute t.i.u.getProcessOutputAndValue
    on the given process with the given arguments """
    return lambda x: twisted.internet.utils.getProcessOutputAndValue(process, args)
   

class Error(Exception):
  """Base class for errors from this module."""


class SvnException(Error):
  """Some problem connecting to subversion"""

  def __init__(self, message):
    Error.__init__(self, message)


def url_join(*args):
    """Join any arbitrary strings into a forward-slash delimited list.
    Do not strip leading / from first element, nor trailing / from last element."""
    if len(args) == 0:
        return ""

    if len(args) == 1:
        return str(args[0])

    else:
        args = [str(arg).replace("\\", "/") for arg in args]

        work = [args[0]]
        for arg in args[1:]:
            if arg.startswith("/"):
                work.append(arg[1:])
            else:
                work.append(arg)

        joined = reduce(os.path.join, work)

    return joined.replace("\\", "/")


if __name__ == '__main__':
  sys.exit('This is not meant to be run as a standalone program. Exiting.')