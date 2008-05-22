#!/usr/bin/env python

import unittest
import os
import popen2
import commands
import time
import urllib
import timeit

import test_all

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
            test_all.getRootDir(),
            'test',
            'test_config.yml'
        )
        
        test_config = open(self.test_config_path, 'w')        
        
        real_config = open(os.path.join(test_all.getRootDir(), 'config.yml')).readlines()
        
        for line in real_config:
            if line.startswith('svn:'):
                test_config.write(line + '\n')
        
        test_config.close()
        

    def tearDown( self ):
        
        # if we've started a Longhouse instance, shut it down
        if hasattr(self, 'pid'):
            
            if str(self.pid) is 'd':
                os.chdir(test_all.getRootDir()) # change to the root so the shutdown script works
                success = commands.getstatusoutput(os.path.join(test_all.getRootDir(), 'shutdown.py'))
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

    def _startLonghouse ( self ):
        
        return popen2.Popen3(
            os.path.join(
                test_all.getRootDir(), 
                'run.py ' + self.test_config_path
            )
        )
        

    def testRunNotDaemonized( self ):
        """Run Longhouse as a normal process (not daemonized)"""
        # TODO: make this and other tests not use time.sleep, so they finish in the minimum time possible
        port = 4321
    
        config_params = [
            'port: ' + str(port),
            'daemonized: false',
        ]
    
        self._addToConfigYml(config_params)
    
        p = self._startLonghouse()
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
    
        p = self._startLonghouse()
        self.pid = 'd' # p.pid would be the wrong pid
    
        time.sleep(4)
    
        try:
            page = urllib.urlopen('http://localhost:' + str(port) + '/').read()
        except IOError:
            self.fail('Could not load Longhouse home page')


    def testMinStartupTime( self ):
        """Test that Longhouse starts up in a minimum amount of time (not daemonized)"""
        
        MIN_STARTUP_TIME = 2 # seconds
        
        port = 4321
    
        config_params = [
            'port: ' + str(port),
            'daemonized: false',
        ]
    
        self._addToConfigYml(config_params)
    
        start_time = time.time()
        
        p = self._startLonghouse()
        
        while(True):
            try:
                page = urllib.urlopen('http://localhost:' + str(port) + '/').read()
            except IOError:
                # hasn't started yet, keep waiting
                time.sleep(0.1)
                continue
            else:
                # finally started!
                self.pid = p.pid
                break
                
        end_time = time.time()
        execution_time = end_time - start_time
        
        self.failIf(execution_time > MIN_STARTUP_TIME, \
            'Longhouse took longer than %s seconds to start (took %s seconds)' % (MIN_STARTUP_TIME, execution_time))
        
    def testMinStartupTimeDaemonized( self ):
        """Test that Longhouse starts up in a minimum amount of time (daemonized)"""

        MIN_STARTUP_TIME = 2 # seconds

        port = 4321

        config_params = [
            'port: ' + str(port),
            'daemonized: true',
        ]

        self._addToConfigYml(config_params)

        start_time = time.time()

        p = self._startLonghouse()

        while(True):
            try:
                page = urllib.urlopen('http://localhost:' + str(port) + '/').read()
            except IOError:
                # hasn't started yet, keep waiting
                time.sleep(0.1)
                continue
            else:
                # finally started!
                self.pid = 'd'
                break

        end_time = time.time()
        execution_time = end_time - start_time

        self.failIf(execution_time > MIN_STARTUP_TIME, \
            'Longhouse took longer than %s seconds to start (took %s seconds)' % (MIN_STARTUP_TIME, execution_time))


if __name__ == "__main__":
    unittest.main()


