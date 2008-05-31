#!/usr/bin/env python

import unittest
import os

def suite(): 
    
    # list all the modules to test here
    modules_to_test = [ 
        'test_startup'
    ]

    alltests = unittest.TestSuite()
    
    # import each module and add its tests to alltests
    for module in map(__import__, modules_to_test):
        alltests.addTest(unittest.findTestCases(module))
    
    # also add tests in this module
    # TODO: can we make this simpler?
    
    #alltests.addTest(unittest.makeSuite(StartAndStop))
    
    return alltests

def getRootDir():
    
    return os.path.dirname(
        os.path.abspath(
            os.path.dirname(
                os.path.realpath(__file__))))

       
if __name__ == '__main__':
    
    import sys
    import os


    EXTRA_PATHS = [
        getRootDir(),
        os.path.realpath(__file__), # should be /test
        os.path.join(getRootDir(), 'src'),
        os.path.join(getRootDir(), 'lib'),
    ]

    sys.path = EXTRA_PATHS + sys.path
    
    
    unittest.main(defaultTest='suite')
