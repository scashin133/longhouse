# Modifying or Creating Business Objects #

In an effort to make generation of business objects easier for developers, there is an automated system for building all of the business objects.  First discussed is some basic architecture and then how to actually use it.

## Architecture ##

When developing for longhouse you are first asked to run a script called yamltobo.py.  This is essentially what the script does:

  1. Finds folders inside of /src/bo/yaml/
  1. For each folder:
    1. Read the yaml file
    1. Add what is interpreted from the yaml file to a file of name generated

<folder\_name>

, where folder name is the name of the folder the script is currently evaluating.

This process is also described below:

![http://longhouse.googlecode.com/svn/www/design_diagrams/yamltobo.png](http://longhouse.googlecode.com/svn/www/design_diagrams/yamltobo.png)

## How to change/add ##

### Yaml structure ###

This will require you looking inside of the folder for your generated file and modifying one of its underlying yaml files.  Lets take a look at a section of one of the yaml files:
```
---
describe: field
name: summary
type: string
value: ""
---
```

This is taken from the Project.yaml file inside of the demetrius folder.  The project.yaml file describes the Project business object.  This particular entry is describing what the summary field is.  Lets break it down piece by piece:

```
---
describe: field
```

This is what the particular entry is talking about.  As of right now it understands two values: field or constant.  Field is going to be the most common value used.  It is used for entries that are variable, will be changed.  Constant should be used if your entry is not going to be changing.  For example, in Project.yaml at the top constant is used.
```
name: summary
```
Name is the name of your varialbe.  This can be whatever you wish but make sure that it is not the same as another entry in this yaml file.
```
type: string
```
What type of variable is this entry?  This entry is going to be the most different from entry to entry.  There are 3 core "types" that can be entered: <primitive type>, <class type>, and arrays.

The primitive types that can be entered are: string and integer.

The class type refers to another business object.  For instance, you can have a variable with **type: Project**.

The array type has a specific syntax to follow, which depends on whether it is an array of primitives or of classes.  If it is an array of primitives the structure is **array\_primitive_<primitive type>_**.  If it is an array of classes the structure is **array_<class name>_**.

```
value: ""
```

This is the default value that this variable will be initialized to.  This value will be initialized to a blank string.  If the variable is an array its default value will normally be **value: "[.md](.md)"**.  If the variable is an object like Project than its default value would be **value: "Project()"**.

### Making a new generated file ###

When developing for longhouse requires the addition of a new generated file, simply add a new folder in /src/bo/yaml.  Than populate that folder with yaml files describe the business objects that will go inside of the modules.

### Something that can't be describe through YAML ###

You are wanting to add a new piece of functionality to a business object, but it can't be described in the yaml.  That is no problem.  Inside of /src/bo/ are two sets of files: the generated modules that are created from the script and their subclasses.  These subclasses are there for that exact reason.  If you look there are already some fields and functions in demetrius\_pb.