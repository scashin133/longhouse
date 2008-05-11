#!/usr/bin/env python

# importing standard python modules
import os,sys
from os.path import join
import copy
import re

# Adding longhouse modules to path
DIR_PATH = os.path.abspath(os.path.dirname(os.path.split(os.path.realpath(__file__))[0]))

EXTRA_PATHS = [
    DIR_PATH,
    os.path.join(DIR_PATH, 'scripts', 'field_helpers'),
    os.path.join(DIR_PATH, 'lib', 'yaml', 'lib')
]

sys.path = EXTRA_PATHS + sys.path


import yaml
from field_helpers import FieldHelpers


global actions

actions = {}

def searchForHandler(target_class):
    action_regex = "handle_(.*)"
    action_pattern = re.compile(action_regex)
    for method in dir(target_class):
        m = re.match(action_pattern, method)
        if m:
            action_name = m.group(1)
            actions[action_name] = getattr(target_class, method)


def indent(num_of_spaces):
    space_str = ""
    for num in range(num_of_spaces):
        space_str = space_str + "\t"
    return space_str

def check_integrity(dict):
    """
    Check the integrity of the values found in the yaml files
    and provide fixes if possible.
    For example, string values should never be empty but instead
    double quotes.
    """
    if (dict['type'] == 'string') and (dict['value'] == None or dict['value'] == ''):
        dict['value'] = '""'

def handle_constant(dict):
    return indent(1) + dict['name'] + indent(1) + "=" + indent(1) + str(dict['value']) + "\n"


def handle_init(dict):
    variable_line = indent(2) + "self." + dict['name'] + "_ = " + str(dict['value']) + "\n"
    has_line = indent(2) + "self.has_" + dict['name'] + "_ = 0\n"
    return variable_line + has_line


def handle_field_type(dict):    
    return handle_init(dict), actions[dict['type']](FieldHelpers(actions),dict)


def handle_primitive_to_xml(dict):
    to_xml = indent(2) + "to_xml += \"<field name=\'" + dict["name"] + "\'>\"\n"
    to_xml += indent(2) + "to_xml += str(self." + dict["name"] + "())\n"
    to_xml += indent(2) + "to_xml += \"</field>\"\n"
    return to_xml


def handle_array_to_xml(dict):
    to_xml = indent(2) + "to_xml += \"<field name=\'" + dict["name"] + "\'>\"\n"
    to_xml += indent(2) + "to_xml += \"<field-list>\"\n"
    if(dict["type"].find("_primitive") != -1):
        to_xml += indent(2) + "for item in self." + dict["name"] + "_list():\n"  
        to_xml += indent(3) + "to_xml += \"<field>\"\n"
        to_xml += indent(3) + "to_xml += str(item)\n"
        to_xml += indent(3) + "to_xml += \"</field>\"\n"
    else:
        to_xml += indent(2) + "for item in self." + dict["name"] + "_list():\n"
        to_xml += indent(3) + "to_xml += \"<field>\"\n"
        to_xml += indent(3) + "to_xml += item.to_xml()\n"
        to_xml += indent(3) + "to_xml += \"</field>\"\n"
    to_xml += indent(2) + "to_xml += \"</field-list>\"\n"
    to_xml += indent(2) + "to_xml += \"</field>\"\n"
    return to_xml

def handle_class_to_xml(dict):
    to_xml = indent(2) + "to_xml += \"<field name=\'" + dict["name"] + "\'>\"\n"
    to_xml += indent(2) + "to_xml += " + dict["name"] + ".to_xml()\n"
    to_xml += indent(2) + "to_xml += \"</field>\"\n"
    return to_xml


def generate_to_xml(dicts, class_name):
    id = "\"\""
    inner_xml = ""
    for data in dicts:
        if data is not None:
            if data['describe'] == "field":
                try:
                    if data['primary']:
                        id = "str(self." + data["name"] + "())"
                except KeyError:
                    pass
                if data['type'].find("array_") != -1:
                    inner_xml += handle_array_to_xml(data)
                else:
                    if data['type'].find("class_") != -1:
                        inner_xml += handle_class_to_xml(data)

                    else:
                        inner_xml += handle_primitive_to_xml(data)
                    
    to_xml = indent(1) + "def to_xml(self):\n"
    to_xml += indent(2) + "to_xml = \"<" + class_name + " id=\'\" + " + id + " + \"\'>\"\n"
    to_xml += indent(2) + "to_xml += \"<field-list>\"\n"
    to_xml += inner_xml
    to_xml += indent(2) + "to_xml += \"</field-list>\"\n"
    to_xml += indent(2) + "to_xml += \"</" + class_name + ">\"\n"
    to_xml += indent(2) + "return to_xml\n\n"
    
    to_xml += indent(1) + "def to_pretty_xml(self):\n"
    # horrible ugly hack alert
    # TODO: make this less horrible, it hurts me to look at it
    to_xml += indent(2) + "return minidom.parseString(self.to_xml()).toprettyxml()[len('<?xml version=\"1.0\" ?>')+1:]\n\n"
    return to_xml


def handle_array_from_xml(data,indent_level=4):
    from_xml = indent(indent_level) + "array_field_list = field.firstChild.childNodes\n"
    from_xml += indent(indent_level) + "for array_field in array_field_list:\n"
    if(data["type"].find("_primitive") != -1):
        primType = data["type"][16:]
        if(primType == "integer"):
            from_xml += indent(indent_level + 1) + "bo.add_" + data['name'] + "(int(array_field.firstChild.nodeValue.encode('ascii', 'replace')))\n"
        else:
            from_xml += indent(indent_level + 1) + "bo.add_" + data['name'] + "(array_field.firstChild.nodeValue.encode('ascii', 'replace'))\n"
        
    else:
        # Taking out array_ beginning PLEASE CHANGE UGLY UGLY UGLY
        class_name = data["type"][6:]
        from_xml += indent(indent_level + 1) + "bo." + data['name'] + "_.append(" + class_name + ".FromXML(array_field.firstChild.to_xml[len('<?xml version=\"1.0\" ?>'):]))\n"
    return from_xml

def handle_class_from_xml(data, indent_level=4):
    # Taking out class_ beginning PLEASE CHANGE UGLY UGLY UGLY
    class_name = data["type"][6:]
    from_xml = indent(indent_level) + "bo." + data['name'] + "_ = " + class_name + ".FromXML(field.firstChild)\n"
    return from_xml

def handle_primitive_from_xml(data, indent_level=4):
    if(data['type'] == "integer"):
        from_xml = indent(indent_level) + "bo.set_" + data['name'] + "(int(field.firstChild.nodeValue.encode('ascii', 'replace')))\n"
    else:
        from_xml = indent(indent_level) + "bo.set_" + data['name'] + "(field.firstChild.nodeValue.encode('ascii', 'replace'))\n"
    
    return from_xml

def generate_from_xml(dicts, class_name, module_name):
    from_xml = indent(1) + "# Takes in a valid xml string and returns a " + class_name + " business object\n"
    from_xml += indent(1) + "def from_xml(bo_topopulate, string_of_xml):\n"
    from_xml += indent(2) + "dom = minidom.parseString(string_of_xml)\n"
    from_xml += indent(2) + "field_list = dom.documentElement.firstChild\n"
    from_xml += indent(2) + "bo = bo_topopulate\n"
    from_xml += indent(2) + "fields = field_list.childNodes\n"
    from_xml += indent(2) + "for field in fields:\n"
    from_xml += indent(3) + "try:\n"
    for data in dicts:
        if data is not None:
            if data['describe'] == "field":
                from_xml += indent(4) + "if field.getAttribute(\"name\") == \"" + data['name'] + "\":\n"
                if data['type'].find("array_") != -1:
                    from_xml += handle_array_from_xml(data, 5)
                else:
                    if data['type'].find("class_") != -1:
                        from_xml += handle_class_from_xml(data, 5)
                    else:
                        from_xml += handle_primitive_from_xml(data, 5)
    # TODO: except AttributeError:pass
    from_xml += indent(3) + "except AttributeError: pass\n"
    from_xml += indent(2) + "dom.unlink()\n"
    from_xml += indent(2) + "return bo\n\n"
    from_xml += indent(1) + "FromXML = staticmethod(from_xml)\n\n"
    return from_xml

def parse_dict(dicts, class_name, module_name):
    fields = ""
    constants = ""
    to_xml = generate_to_xml(dicts, class_name)
    from_xml = generate_from_xml(dicts, class_name, module_name)
    init_method = indent(1) + "def __init__(self):\n"
    for data in dicts:
        if data is not None:
            check_integrity(data)
            if data['describe'] == "constant":
                constants = constants + handle_constant(data)
            elif data['describe'] == "field":
                init_line, field_methods = handle_field_type(data)
                fields = fields + field_methods
                init_method = init_method + init_line
                
            
    return init_method, constants, fields, to_xml, from_xml


def construct_bo_class(class_name, init_method, constants, fields, to_xml, from_xml):
    str_class = "class " + class_name + "(object):\n"
    str_class += constants
    str_class += init_method + "\n"
    str_class += fields
    str_class += to_xml
    str_class += from_xml
    return str_class


def generate_bo_file(path, module_name):
    bo_file_contents = ""
    for filename in os.listdir(path):
        if(re.compile("(/\.)").search(os.path.join(path, filename)) is not None):
            continue
        print "file parsing: " + os.path.join(path, filename)
        stream = file(os.path.join(path, filename), 'r')
        all_data = yaml.load_all(stream)
        data_array = []
        for data in all_data:
            data_array.append(data)
        class_name, ext = os.path.splitext(filename)
        init_method, constants, fields, to_xml, from_xml = parse_dict(data_array, class_name, module_name)
        bo_file_contents += construct_bo_class(class_name, init_method, constants, fields, to_xml, from_xml)
    return bo_file_contents



def imports(module_name):
    """
    return the import statements that should appear at the top
    of every generated file
    """
    import_string = "from xml.dom import minidom\n"
    return import_string

if __name__ == '__main__':

    searchForHandler(FieldHelpers)

    for root, dirs, files in os.walk(os.path.join(DIR_PATH, 'bo', 'yaml')):
        for dir_name in dirs:
            if(re.compile("(/\.)").search(os.path.join(root,dir_name)) is not None):
                continue
            bo_file = open(os.path.join(DIR_PATH, 'bo', "generated_"+dir_name+".py"), "w+")
            bo_file.write(imports(dir_name))
            bo_file.write(generate_bo_file(os.path.join(root, dir_name), dir_name))
            bo_file.close
        
