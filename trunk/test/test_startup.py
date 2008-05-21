#!/usr/bin/env python

import unittest
import os
import popen2
import commands
import time
import urllib

import alltests

class StartAndStop(unittest.TestCase):
    """Test if Longhouse is configured correctly 
    to be able to start and shut down."""

    def setUp( self ):
        
        # make a test_config.yml file
        # and populate it with the "svn" field
        # from the real config.yml
        
        # To successfully launch, Longhouse needs more fields than this.
        # They can be added using _addToConfigYml
        
        self.test_config_path = os.path.join(
            alltests.getRootDir(),
            'test',
            'test_config.yml'
        )
        
        test_config = open(self.test_config_path, 'w')        
        
        real_config = open(os.path.join(alltests.getRootDir(), 'config.yml')).readlines()
        
        for line in real_config:
            if line.startswith('svn:'):
                test_config.write(line + '\n')
        
        test_config.close()
        

    def tearDown( self ):
        
        # if we've started a Longhouse instance, shut it down
        if hasattr(self, 'pid'):
            
            if str(self.pid) is 'd':
                os.chdir(alltests.getRootDir()) # change to the root so the shutdown script works
                success = commands.getstatusoutput(os.path.join(alltests.getRootDir(), 'shutdown.py'))
            else:
                success = commands.getstatusoutput("kill -9 " + str(self.pid))
                
            if not success[0] is 0:
                print success
                self.fail('Failed to shutdown Longhouse')

        # remove the test config file
        os.remove(self.test_config_path)


    def _addToConfigYml( self, param_list ):
        
        test_config = open(self.test_config_path, 'a')
        
        for param in param_list:
            test_config.write(param + '\n')
            
        test_config.close()

    def testRunNotDaemonized( self ):
        """Run Longhouse as a normal process (not daemonized)"""
    
        port = 4321
    
        config_params = [
            'port: ' + str(port),
            'daemonized: false',
        ]
    
        self._addToConfigYml(config_params)
    
        p = popen2.Popen3(os.path.join(alltests.getRootDir(), 'run.py ' + self.test_config_path))
        self.pid = p.pid
    
        time.sleep(4)
        
        try:
            page = urllib.urlopen('http://localhost:' + str(port) + '/').read()
        except IOError:
            self.fail('Could not load Longhouse home page')
            
            
    def testRunDaemonized( self ):
        """Run Longhouse daemonized"""

        port = 4321

        config_params = [
            'port: ' + str(port),
            'daemonized: true',
            'logging: true'
        ]

        self._addToConfigYml(config_params)

        p = popen2.Popen3(os.path.join(alltests.getRootDir(), 'run.py ' + self.test_config_path))
        self.pid = 'd' # p.pid would be the wrong pid

        time.sleep(4)

        try:
            page = urllib.urlopen('http://localhost:' + str(port) + '/').read()
        except IOError:
            self.fail('Could not load Longhouse home page')


if __name__ == "__main__":
    unittest.main()


