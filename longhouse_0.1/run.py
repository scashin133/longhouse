#!/usr/bin/env python

def createDaemon(UMASK, MAXFD, DAEMON_LOG, ROOT_DIR, REDIRECT_TO):
   """Detach a process from the controlling terminal and run it in the
   background as a daemon.
   """

   try:
      # Fork a child process so the parent can exit.  This returns control to
      # the command-line or shell.  It also guarantees that the child will not
      # be a process group leader, since the child receives a new process ID
      # and inherits the parent's process group ID.  This step is required
      # to insure that the next call to os.setsid is successful.
      pid = os.fork()
   except OSError, e:
      raise Exception, "%s [%d]" % (e.strerror, e.errno)

   if (pid == 0):   # The first child.
      # To become the session leader of this new session and the process group
      # leader of the new process group, we call os.setsid().  The process is
      # also guaranteed not to have a controlling terminal.
      os.setsid()

      # Is ignoring SIGHUP necessary?
      #
      # It's often suggested that the SIGHUP signal should be ignored before
      # the second fork to avoid premature termination of the process.  The
      # reason is that when the first child terminates, all processes, e.g.
      # the second child, in the orphaned group will be sent a SIGHUP.
      #
      # "However, as part of the session management system, there are exactly
      # two cases where SIGHUP is sent on the death of a process:
      #
      #   1) When the process that dies is the session leader of a session that
      #      is attached to a terminal device, SIGHUP is sent to all processes
      #      in the foreground process group of that terminal device.
      #   2) When the death of a process causes a process group to become
      #      orphaned, and one or more processes in the orphaned group are
      #      stopped, then SIGHUP and SIGCONT are sent to all members of the
      #      orphaned group." [2]
      #
      # The first case can be ignored since the child is guaranteed not to have
      # a controlling terminal.  The second case isn't so easy to dismiss.
      # The process group is orphaned when the first child terminates and
      # POSIX.1 requires that every STOPPED process in an orphaned process
      # group be sent a SIGHUP signal followed by a SIGCONT signal.  Since the
      # second child is not STOPPED though, we can safely forego ignoring the
      # SIGHUP signal.  In any case, there are no ill-effects if it is ignored.
      #
      # import signal           # Set handlers for asynchronous events.
      # signal.signal(signal.SIGHUP, signal.SIG_IGN)

      try:
         # Fork a second child and exit immediately to prevent zombies.  This
         # causes the second child process to be orphaned, making the init
         # process responsible for its cleanup.  And, since the first child is
         # a session leader without a controlling terminal, it's possible for
         # it to acquire one by opening a terminal in the future (System V-
         # based systems).  This second fork guarantees that the child is no
         # longer a session leader, preventing the daemon from ever acquiring
         # a controlling terminal.
         pid = os.fork()    # Fork a second child.
      except OSError, e:
         raise Exception, "%s [%d]" % (e.strerror, e.errno)

      if (pid == 0):    # The second child.
         # Since the current working directory may be a mounted filesystem, we
         # avoid the issue of not being able to unmount the filesystem at
         # shutdown time by changing it to the root directory.
         
         #os.chdir(ROOT_DIR) # we do this in main() now
         
         # We probably don't want the file mode creation mask inherited from
         # the parent, so we give the child complete control over permissions.
         os.umask(UMASK)
      else:
         # exit() or _exit()?  See below.
         os._exit(0)    # Exit parent (the first child) of the second child.
   else:
      # exit() or _exit()?
      # _exit is like exit(), but it doesn't call any functions registered
      # with atexit (and on_exit) or any registered signal handlers.  It also
      # closes any open file descriptors.  Using exit() may cause all stdio
      # streams to be flushed twice and any temporary files may be unexpectedly
      # removed.  It's therefore recommended that child branches of a fork()
      # and the parent branch(es) of a daemon use _exit().
      os._exit(0)   # Exit parent of the first child.

   # Close all open file descriptors.  This prevents the child from keeping
   # open any file descriptors inherited from the parent.  There is a variety
   # of methods to accomplish this task.  Three are listed below.
   #
   # Try the system configuration variable, SC_OPEN_MAX, to obtain the maximum
   # number of open file descriptors to close.  If it doesn't exists, use
   # the default value (configurable).
   #
   # try:
   #    maxfd = os.sysconf("SC_OPEN_MAX")
   # except (AttributeError, ValueError):
   #    maxfd = MAXFD
   #
   # OR
   #
   # if (os.sysconf_names.has_key("SC_OPEN_MAX")):
   #    maxfd = os.sysconf("SC_OPEN_MAX")
   # else:
   #    maxfd = MAXFD
   #
   # OR
   #
   # Use the getrlimit method to retrieve the maximum file descriptor number
   # that can be opened by this process.  If there is not limit on the
   # resource, use the default value.
   #
   import resource      # Resource usage information.
   maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
   if (maxfd == resource.RLIM_INFINITY):
      maxfd = MAXFD

   # Iterate through and close all file descriptors.
   for fd in range(0, maxfd):
      try:
         os.close(fd)
      except OSError:   # ERROR, fd wasn't open to begin with (ignored)
         pass

   # Redirect the standard I/O file descriptors to the specified file.  Since
   # the daemon has no controlling terminal, most daemons redirect stdin,
   # stdout, and stderr to /dev/null.  This is done to prevent side-effects
   # from reads and writes to the standard I/O file descriptors.

   # This call to open is guaranteed to return the lowest file descriptor,
   # which will be 0 (stdin), since it was closed above.
   os.open(REDIRECT_TO, os.O_RDWR)  # standard input (0)

   # Duplicate standard input to standard output and standard error.
   os.dup2(0, 1)            # standard output (1)
   os.dup2(0, 2)            # standard error (2)

   return(0)


def main():

    """
    Try to load the config file
    (config.yml or config.yaml)
    """
    try:
        config = yaml.load(open('../config.yml'))
    except IOError:
        """
        Maybe some silly person named it config.yaml instead...
        """
        try:
            config = yaml.load(open('../config.yaml'))
        except IOError:
            """
            Couldn't find config file under either name.
            """
            print "Error: couldn't load config.yml at " + \
                os.path.join(os.getcwd(), '..', 'config.yml')
            sys.exit(1)

    """
    Should we run in daemonized mode?
    Not required.
    """
    DAEMONIZED = config.get('daemonized')
    if DAEMONIZED == None or DAEMONIZED == "":
        DAEMONIZED = False

    if(DAEMONIZED):
    
        """
        Get the umask (file mode creation mask of the daemon)
        Not required.
        """
        UMASK = config.get('umask')
        if UMASK == None or UMASK == "":
            UMASK = 7
        
        """
        Get maximum number of available file descriptors.
        Not required.
        """
        MAXFD = config.get('maxfd')
        if MAXFD == None or MAXFD == "":
            MAXFD = 1024
    
        """
        Get the daemon log file.
        Not required.
        """
        DAEMON_LOG = config.get('daemon_log')
        if DAEMON_LOG == None or DAEMON_LOG == "":
            DAEMON_LOG = os.path.join(ROOT_DIR, 'logs', 'createDaemon.log')

    """
    Should we log?
    Not required.
    """
    LOGGING = config.get('logging')
    if LOGGING == None or LOGGING == "":
        LOGGING = False
  
    """
    If we're logging, get the log file.
    If we're not logging, just throw output to std out
    Not required.
    """
    if(LOGGING):  
        LOGFILE = config.get('logfile')
        if LOGFILE == None or LOGFILE == "":
            LOGFILE = os.path.join(ROOT_DIR, 'logs', 'longhouse.log')
    else:
        LOGFILE = None
        

    """
    Get the port number.
    Not required.
    """
    PORT = config.get('port')
    if PORT == None or PORT == "":
        PORT = 8080

    """
    Get the svn location.
    Required.
    """
    SVN_LOC = config.get('svn')
    if SVN_LOC == None or SVN_LOC == "":
        print 'Error: svn location not specified in config.yml'
        sys.exit(1)
    constants.SVN_LOC = SVN_LOC


    """
    The standard I/O file descriptors are redirected 
    to /dev/null by default.
    """
    if (hasattr(os, "devnull")):
       REDIRECT_TO = os.devnull
    else:
       REDIRECT_TO = "/dev/null"

    if(DAEMONIZED):
        """
        Create a daemon and write to the daemon log file.
        """
        print 'Longhouse daemon launching on port', PORT
        retCode = createDaemon(UMASK, MAXFD, DAEMON_LOG, ROOT_DIR, REDIRECT_TO)
        procParams = """
        return code = %s
        process ID = %s
        parent process ID = %s
        process group ID = %s
        session ID = %s
        user ID = %s
        effective user ID = %s
        real group ID = %s
        effective group ID = %s
        """ % (retCode, os.getpid(), os.getppid(), os.getpgrp(), os.getsid(0), os.getuid(), os.geteuid(), os.getgid(), os.getegid())
        print 'opening', DAEMON_LOG
        open(DAEMON_LOG, "w").write(procParams + "\n")


    """
    Start logging
    """

    if LOGGING:
        log.startLogging(open(LOGFILE, "w+"), 0)

    if not DAEMONIZED:
        log.startLogging(sys.stdout)



    """
    Run longhouse!
    """
    codesite.main(PORT, DAEMONIZED)

    """
    Longhouse shut itself down
    """
    if(DAEMONIZED):
        sys.exit(retCode)
        
        
if __name__ == '__main__':

    # first patch up the path

    import sys
    import os

    # the directory this file is in
    # should be the root dir
    ROOT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

    EXTRA_PATHS = [
        os.path.join(ROOT_DIR, 'src'), # /src
        os.path.join(ROOT_DIR, 'lib'), # /lib
    ]

    sys.path = EXTRA_PATHS + sys.path     


    # make sure some directories exist

    dirs = [
        'src/storage/unversioned',
        'src/storage/working_copies',
        'logs',
    ]
    
    for dir in dirs:
        try:
            os.makedirs(dir)
        except OSError:
            continue


    # now we can import from /src and /lib
    # time to start Longhouse


    from main import codesite
    import yaml

    from framework import constants
    
    from twisted.python import log
        
    constants.WORKING_DIR = os.path.join( ROOT_DIR, 'src' )
    os.chdir(constants.WORKING_DIR)
        
    main()
    
    
    

