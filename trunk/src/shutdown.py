#!/usr/bin/env python
import os
import re
import sys
import commands

import yaml

#TODO: softer shutdown


"""
Try to load the config file
(config.yml or config.yaml)
"""
try:
    config = yaml.load(open('config.yml'))
except IOError:
    """
    Maybe some silly person named it config.yaml instead...
    """
    try:
        config = yaml.load(open('config.yaml'))
    except IOError:
        """
        Couldn't find config file under either name.
        """
        print "Error: couldn't load config.yml at " + \
            os.path.join(os.getcwd(), 'config.yml')
        sys.exit(1)
        
"""
Get the daemon log file.
"""
DAEMON_LOG = config.get('daemon_log')
if DAEMON_LOG == None or DAEMON_LOG == "":
    DAEMON_LOG = "createDaemon.log"
    
"""
Load the log file and retrieve the port number
"""
try:
    log = open(DAEMON_LOG).read()
except IOError:
    print "Daemon log could not be opened"
    sys.exit(1)

try:
    pid = re.search("process ID = (\d+)", log).group(1)
except AttributeError:
    print 'Process number not found in daemon log. ' + \
        'Is Longhouse running?'
    sys.exit(1)

"""
Kill the process.
"""
success = commands.getstatusoutput("kill " + pid)

if(success[0] == 0):
    """
    Successful shutdown.
    Clear the daemon log so we don't try
    to kill the process again and kill something
    other than longhouse
    """
    log = open(DAEMON_LOG, "w")
    log.close()
    print 'Longhouse daemon shut down.'
else:
    print 'Error.'


