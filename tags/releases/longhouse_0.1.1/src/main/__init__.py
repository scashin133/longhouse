import sys, os, string

# ensure minimum python version

min_version = [2, 5, 1]

version = string.split(string.split(sys.version)[0], ".")
if map(int, version) < min_version:
    print 'Error: Longhouse requires Python', \
        string.join(map(str, min_version), '.'), \
        'or higher. You are running Python', \
        string.join(map(str, version), '.')
    sys.exit(1)
    

# ensure hashlib is installed

try:
    import hashlib
except ImportError:
    print 'Error: you must have hashlib installed'
    sys.exit(1)

