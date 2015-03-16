# How to Install and Run Longhouse #

## Quick and Easy Install Guide ##

  1. Download and install [Python 2.5 or higher](http://www.python.org)
  1. Download and install [Subversion](http://subversion.tygris.org)
  1. Download the latest release from [the Downloads section](http://code.google.com/p/longhouse/downloads/list)
  1. Unarchive the release and place the root directory wherever you want
  1. [Change default settings, if necessary in your environment](InstallLonghouse#Configuration.md)
  1. Run the file `run.py` in the root directory

Need more info? Refer to the in-depth guide below.

## In-Depth Guide ##

### Table of Contents ###


  1. [Dependencies](InstallLonghouse#Dependencies.md)
  1. [Installation](InstallLonghouse#Installation.md)
  1. [Configuration](InstallLonghouse#Configuration.md)
  1. [Generate Code](InstallLonghouse#Generate_Code.md)
  1. [Run](InstallLonghouse#Run.md)
  1. [Use Longhouse](InstallLonghouse#Use_Longhouse.md)
  1. [Shut Down](InstallLonghouse#Shut_Down.md)

### Dependencies ###

Longhouse requires:
  * Python - http://www.python.org/
    * Version 2.5 or higher is required
  * Subversion - http://subversion.tigris.org/
  * Twisted - http://twistedmatrix.com/
    * Version 8.0.1 or higher is required
    * Note: at the time or writing, Longhouse will not work in daemonized mode if using Twisted 8.1.0
    * Recommended download: http://tmrc.mit.edu/mirror/twisted/Twisted/8.0/Twisted-8.0.1.tar.bz2
  * zope.interface
    * Comes packaged with Zope3, although only zope.interface is needed by Longhouse
    * Recommended download: http://www.zope.org/Products/ZopeInterface/3.3.0/zope.interface-3.3.0.tar.gz
  * PyYaml
    * Recommended download: http://pyyaml.org/download/pyyaml/PyYAML-3.05.tar.gz


You must install both Python and Subversion before installing Longhouse.

There are three options for installing the required packages (Twisted, zope.interface, and PyYaml)

**You don't need to do any of these if you downloaded a release from the [Downloads section](http://code.google.com/p/longhouse/downloads/list). The archived releases should come with all necessary libs.**

  1. Install the packages as described in their respective installation procedures. This will make them available to all Python programs, including Longhouse.
  1. Extract the packages' source into Longhouse's `/lib` directory. This will make them available exclusively to Longhouse. This is useful if, say, you wanted to use a different version of Twisted for another project. Now your `/lib` directory should be structured like the following...
```
lib/
	ezt/
		...
	twisted/
		application/
		web/
		...
	yaml/
		__init__.py
		composer.py
		...
	zope/
		__init__.py
		interface/
			...
```
  1. Go to the Longhouse download section to download the longhouse dependencies tarball. Extract this into Longhouse's `/lib` directory.

**IMPORTANT NOTE:** Some methods of distributing Python 2.5 do not seem to include the `hashlib` library, which will create an error when you attempt to run Longhouse. Darwinports is known to have this problem at the time of writing. If you experience this issue, you may either install a standard release of 2.5.2 from [python.org](http://www.python.org) or obtain `hashlib` from [here](http://pypi.python.org/pypi/hashlib/20060408a).

Once you install Subversion, take note of where the `svn` command is located. We will need this later. A common location is `/usr/local/bin/svn`. On Unix systems, run the command `which svn` to find where `svn` is located.

### Installation ###

Download the latest Longhouse install from Longhouse's Google Code site, at http://code.google.com/p/longhouse/. Decompress the archive and place the source files where you'd like them to reside - the specific location doesn't matter for the purposes of running the software. Inside the root folder you should see a `lib` folder, a `src` folder, and several files, listed below in the Configuration section.

### Configuration ###

Longhouse requires a configuration file in order to run properly. Navigate to the directory that you copied the Longhouse source files to. You should see several files, including:
  * `INSTALL`
  * `config.yml.example`
  * `run.py`
  * `shutdown.py`

You're going to need to create a config file in order to ensure that Longhouse runs properly. The install should contain an example config file, named `config.yml.example`, so you may simply create a new config file from the example config file. On Unix systems you can achieve this by running the command `cp config.yml.example config.yml`.

The Longhouse config file has four values that need to be present in order for Longhouse to run. The first value to specify is the port you want the Longhouse server to run on. Choose whatever value you want that isn't being used by any other web services running on your machine. Some common ports to use are port `80`, `8000` or `8080`. We recommend simply using `8080` unless there is another program using it, or another reason to not use it. The line describing the port looks like:

`port: 8080`

The next value you're going to define is whether you want the process to be daemonized or not. If you use the value `true`, when you run Longhouse it will spawn a separate process, so you'll be free to close your Python environment or command-line invocation. In this case you can use the `shutdown.py` script to shut down Longhouse. If you use `false`, it behaves like a regular Python application, running while your invocation of the Python runtime environment is active. So, this line looks like the following:

`daemonized: true`

or

`daemonized: false`

Next, specify whether you want Longhouse to log itself to a log file or not. This is crucial if you specified `daemonized: true`; if you run Longhouse as a separate process you will need to specify `logging: true` to have any output from Longhouse.

`logging: true`

or

`logging: false`

Finally, specify the location of your `svn` command. For example, mine is located at `/usr/local/bin/svn`, so I'd write:

`svn: /usr/local/bin/svn`

My entire config file is as follows:

`port: 8080`

`daemonized: false`

`logging: true`

`svn: /usr/local/bin/svn`

### Generate Code ###

If you downloaded Longhouse as a release, you may skip this step because all the code you need to run Longhouse has already been generated. However if you checked out the source code directly from the repository you will need to complete one last step before starting the system. Navigate to the `/src/scripts` directory and run `yaml_to_bo.py`. This script reads the files in `/src/bo/yaml` and generates several python modules in `/src/bo` named `generated_*.py`. Without these generated files, Longhouse cannot run.

If you encounter any errors with this step, check our [FAQ/Troubleshooting page](FAQTroubleshoot.md).

### Run ###

Run the file `run.py` in the Longhouse root directory. If all goes well, Longhouse should be running properly. If you encounter any errors, check our [FAQ/Troubleshooting page](FAQTroubleshoot.md).

### Use Longhouse ###

Visit `http://localhost:portnumber/` to test whether Longhouse is running, where `portnumber` is the value you specified for `port` in the `config.yml` file. If you encounter an 'Unable to connect' or similar error, it means Longhouse isn't running on that port for one reason or another. Check our [FAQ/Troubleshooting page](FAQTroubleshoot.md) to find out why.

### Shut Down ###

If you specified `daemonized: true` in the `config.yml` file, you need to run `shutdown.py` to shut Longhouse down. If not, simply exit the program in which you invoked `run.py`.