The following is a walkthrough for creating a release for Longhouse 0.0 from the trunk of the repository.

  1. Check out the code without the .svn directories:
    * `svn export https://longhouse.googlecode.com/svn/trunk/ longhouse_0.0/`
  1. Download, extract, and install dependencies (at the time of writing, 0.1.2 was the newest dependency bundle)
    * `wget http://longhouse.googlecode.com/files/longhouse_dependencies_0.1.2.tar.gz`
    * `tar -xzf longhouse_dependencies_0.1.2.tar.gz`
    * `cp -R longhouse_dependencies_0.1.2/* longhouse_0.0/lib/`
  1. Generate business objects from yaml:
    * `python longhouse_0.0/src/scripts/yaml_to_bo.py`
  1. You may wish to modify the installation instructions:
    * `vim longhouse_0.0/INSTALL`
  1. Package the files
    * tar:   `tar -cf longhouse_0.0.tar longhouse_0.0/`
    * gzip:  `tar -czf longhouse_0.0.tar.gz longhouse_0.0/` 
    * bzip2: `tar -cjf longhouse_0.0.tar.bz2 longhouse_0.0/` 