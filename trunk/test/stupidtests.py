#!/usr/bin/env python

import unittest

class AdditionTestCase(unittest.TestCase):
    
    def runTest( self ):
        assert (2 + 2) == 4, '2 + 2 should equal 4'
        
        
class SubtractionTestCase( unittest.TestCase ):

    def testPositives (self ):
        assert (5 - 3) == 2, '5 - 3 should equal 2'

    def testNegatives ( self ):
        """Subtract a positive number from a negative number"""
        self.assertEqual(-2 - 4, -6)



if __name__ == "__main__":
    unittest.main()


