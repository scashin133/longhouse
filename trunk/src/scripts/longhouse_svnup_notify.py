
"""
This script will be called by the subversion post commit hook
to notify longhouse that it should do a svn up. 
"""

import sys
import urllib

repos_path = sys.argv[1]
rev = sys.argv[2]

#page = urllib.urlopen("http://www.google.com/").read()
#print page

file = open("log.txt", "a")
file.write("""Script run.
repos_path = %s
rev = %s
------------
""" % (repos_path, rev))
