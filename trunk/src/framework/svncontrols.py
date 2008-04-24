import commands
import shutil
import os
from time import strftime
import re
import glob

import twisted.internet.utils
from twisted.internet import reactor, defer

VERBOSE = True

def deferred_helloworld(self):
    d = defer.Deferred()
    reactor.callLater(2, d.callback, 'hello, world!')
    return d

class ProjectSvnUpPage:
    
    def __init__(self, demetrius_persist):
        self.demetrius_persist = demetrius_persist
    
    
    def Handler(self, request):
        print 'svn up handler called'
        self.project = request.postpath[0]
        d = self.demetrius_persist.GetProject(self.project).svn_controller().d_up()
        # TODO: add callback here to update BO
        d.addCallback(self.load_fresh_xml)
        d.addCallback(self.return_msg)
        return d

    def load_fresh_xml(self, *args):
        self.demetrius_persist.GetProject(self.project, fresh=True)

    def return_msg(self, *args):
        return 'Done.'
    

class SvnController:
    
    SUCCESS = 0
    ERROR = 256
    
    CONFLICT_FILES = re.compile('^C\s+(.*)$', re.MULTILINE)
    
    def __init__(self, repository_location, 
                 repository_username,
                 repository_password,
                 svn_location="/usr/local/bin/svn",
                 working_copy_root=""):
        """
        Initialize a new SvnController. Repository location must be specified.
        You may also have to specify the location of the 'svn' command line
        utility, and can optionaly specify a location to check out
        working copies to.
        """
        if VERBOSE:
            print 'constructing working copy root at:', working_copy_root
        
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
        
        self.svn_location = svn_location
        
        if VERBOSE:
            print 'testing newly created svn controller'
        self.d_test()
        
    def d_test(self): 
        """Determine if we can contact the repository."""
        d = self.d_remote_list('/')
        d.addCallback(self._return_success).addCallback(self._print_response)
        d.addErrback(self._print_error)
        return d
    
    def _return_success(self, output):
        if output[2] == self.SUCCESS:
            return True
        else:
            return False
        
    def _print_response(self, response):
        print 'got response:', response
        
    def _print_error(self, error):
        print 'error in deferred:', error
    
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
        if VERBOSE:
            print 'has working copy?', self.is_working_copy(self.working_copy_root)
        return self.is_working_copy(self.working_copy_root)
    
    def d_remote_list(self, dir, ):
        """
        Perform a 'svn list' command on the repository
        """
        if VERBOSE:
            print 'd_remote_list called'
        args = ['list', 
                url_join(self.repository_location, dir),
                '--username', self.repository_username, 
                '--password', self.repository_password]
        
        return twisted.internet.utils.getProcessOutputAndValue(
                    self.svn_location, args)


    def d_checkout(self, repo_dir = '', local_path = '#'):
        """
        Checkout a working copy. If repo_dir is not specified, check out
        the root of the repository. If local_path is not specified, 
        use the previously given working copy root
        TODO: untested
        """
        if VERBOSE:
            print 'd_checkout called'
            
        if local_path == '#':
            local_path = self.working_copy_root
        
        args = ['co', 
                url_join(self.repository_location, repo_dir),
                local_path,
                '--username', self.repository_username, 
                '--password', self.repository_password]
        
        return twisted.internet.utils.getProcessOutputAndValue(
                    self.svn_location, args)


    def d_up_add_commit(self, message="generic Longhouse commit"):
        if VERBOSE:
            print 'd_up_add_commit starting chain'
            
        self.message = message
        d = self._d_cleanup()
        d.addCallback(self.d_up)
        d.addCallback(self._d_add_all)
        d.addCallback(self._d_commit)


    def d_up(self, *args):
        """
        Perform a 'svn up' opperation. By default the 
        path is the working copy root. Handle any bad merges by
        having local changes take priority. 
        """
        if VERBOSE:
            print '_d_up called'
        
        args = ['up', self.working_copy_root]
        
        d = twisted.internet.utils.getProcessOutputAndValue(
                    self.svn_location, args)
        d.addCallback(self._handle_bad_merges)
        
        return d
    
    
    def _d_cleanup(self, *args):
        if VERBOSE:
            print '_d_cleanup called'
        
        args = ['cleanup']
        
        return twisted.internet.utils.getProcessOutputAndValue(
                    self.svn_location, args)
    

    def _d_add_all(self, *args):
        """
        Add the specified file or directory to the repository. It
        will be checked in in the next commit.
        """
        if VERBOSE:
            print '_d_add_all called'

        args = ['add', '--force', self.working_copy_root]
        
        return twisted.internet.utils.getProcessOutputAndValue(
                    self.svn_location, args)


    def _d_commit(self, *args):
        """
        Perform a 'svn commit' command. If no directory is specified, 
        commit the working copy root.
        """
        if VERBOSE:
            print 'd_commit called'
            
        if self.message == None:
            self.message = 'generic Longhouse commit'
        
        args = ['ci', 
                self.working_copy_root, 
                '--username', self.repository_username, 
                '--password', self.repository_password,
                '-m', '"%s"' % self.message]
        
        d = twisted.internet.utils.getProcessOutput(self.svn_location, args)
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
        if VERBOSE:
            print '_handle_bad_merges called, given', output
            
        bad_merges = self.CONFLICT_FILES.findall(output[0])
        
        for bad_merge in bad_merges:
            print 'correcting bad merge on file', bad_merge
            
            # use the .mine file as resolution (local changes take priority)
            shutil.copyfile(bad_merge + '.mine', bad_merge)
            
            # remove the .mine file and both .r* files
            os.remove(bad_merge + '.mine')
            for revision_file in glob.glob(bad_merge + '.r*'):
                os.remove(revision_file)
        

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



def simulate_xml():
    """
    the following method simulates things the xml layer will be doing.
    In practice, the subversion layer (this) will not manipulate the file
    system at all except for checking out a working copy in case one
    does not exist.
    """
    try:
        file = open("wc/file.txt")
        fileExists = True
        file.close()
    except IOError:
        # write a file template to the working copy
        #shutil.copyfile("fileTemplate.txt", "wc/file.txt")
        file = open("wc/file.txt", "w")
        file.write("this is a file")
        file.close()
        # add file.txt to the repository
        svnc.add("wc/file.txt")
        
    # open the file for appending
    file = open("wc/file.txt", "a")
    
    # append to the log file
    datePattern = "%b %d, %Y"
    timePattern = "%I:%M %p"
    writeText = "\nsvn demo run on " + strftime(datePattern) + " at " + strftime(timePattern)
    file.write(writeText)
    file.close()



"""
The field '_instance' along with methods 'initialize()' and 
'get_instance()' represent a singleton pattern. When
longhouse starts up, 'initialize()' should be called to set up
a SvnController object to be used by the rest of the code. Then
whenever the SvnController needs to be used, retrieve it with
the 'get_instance' method. 
"""

_instance = None

def initialize(repository_location, 
                 svn_location="/usr/local/bin/svn",
                 working_copy_root=""):
    global _instance
    _instance = SvnController(repository_location=repository_location,
                             svn_location=svn_location,
                             working_copy_root=working_copy_root) 

def get_instance():
    global _instance
    if _instance == None:
        raise Exception('No SvnController has been initialized. Call \
initialize() before trying to retrieve an instance.')
    return _instance


if __name__ == '__main__':
    """
    Add an entry to the log file (meta/file.txt)
    If a working copy doesn't already exist, check it out first
    """
    
    # create a new svn controller connected to a repository on 
    # the local computer, setting the working copy root
    # TODO: set up some other repository to use
    #svnc = SvnController("file:///repository/svn/svndemo",\
    #                    working_copy_root="wc") 
    initialize("file:///repository/svn/svndemo",\
                        working_copy_root="wc")
    
    svnc = get_instance()
    
    # check if we have a working copy
    # if we don't, check out the repository's 'meta' folder
    # into our specified working copy root ('wc')
    if not svnc.has_working_copy():
        print 'no working copy, checking it out'
        svnc.checkout('meta')
    
    # simulate the xml layer
    # (make some changes to file.txt)    
    simulate_xml()
    
    # check in the changes
    result = svnc.commit(message="logging another run of svncontrols")
    
    if result[0] == SvnController.SUCCESS:
        print "Success!"
    else:
        print "Error", result
    
        