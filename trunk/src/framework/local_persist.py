#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

## LIST OF TYPES TO PASS ('object_type' variable)
## 'project' - Project
## 'user' - User
## 'issue' - Issues metadata
## 'issue_comments' - Issue Comments
## 'user_issue_stars' - User Issue Stars
## 'issue_user_stars' - Issue User Stars
## 'download' - Download metadata
## 'download_comments' - Download comments
## 'wiki' - Wiki page
## 'wiki_metadata' - Wiki metadata
## 'wiki_comments' - Wiki comments

import shutil
import re
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

import constants
from bo import demetrius_pb   
   
DEMETRIUS_PERSIST = None
   
class OBJECT_TYPES:
    PROJECT = 'Project'
    ISSUE = 'Issue'
    ISSUE_COMMENT = 'IssueComment'
    USER_ISSUE_STAR = 'UserIssueStars'
    ISSUE_USER_STAR = 'UserIssueStars'
    USER = 'User'

def init(demetrius_persist):
    """
    Make sure some files are in place if they aren't already.
    """
    
    DEMETRIUS_PERSIST = demetrius_persist
    
    local_storage = os.path.join(constants.WORKING_DIR, constants.LOCAL_STORAGE_ROOT)
    
    local_user_storage = os.path.join(local_storage, constants.LD_USERS)
    if not os.path.exists(local_user_storage):
        users_xml_template = os.path.join(constants.WORKING_DIR, 'templates/storage/users.xml')
        shutil.copy(users_xml_template, local_user_storage)
    
    local_project_storage = os.path.join(local_storage, constants.LD_PROJECTS)
    if not os.path.exists(local_project_storage):
        projects_xml_template = os.path.join(constants.WORKING_DIR, 'templates/storage/projects.xml')
        shutil.copy(projects_xml_template, local_project_storage)
    

def load_item_from_local_disk(object_type, object_id):
    """ TODO: docstring """
    
    # retrieve the path for this object
    path = {
        OBJECT_TYPES.PROJECT : constants.LD_PROJECTS,
        OBJECT_TYPES.USER : constants.LD_USERS
    }.get(object_type, None)
    
    
    if(path) is None:
        raise UnsupportedArtifactException('Attempted to load an invalid artifact :' +
            '\nProject Name: ' + projectname +
            '\nArtifact type: ' + object_type +
            '\nArtifact ID: ' + str(object_id))
        
    # construct the full path
    path = os.path.join(
        constants.WORKING_DIR, constants.LOCAL_STORAGE_ROOT, path)

    object = None
    if object_type == OBJECT_TYPES.PROJECT:
        object = demetrius_pb.Project()
#    elif object_type == OBJECT_TYPES.USER:
#        pass
    # TODO: other object types 
    
    if not object == None:
        # parse!
        handler = SingleObjectLoadSaxHandler(object_type, object_id)
        parser = make_parser()
        parser.setContentHandler(handler)
        print 'about to parse', path
        parser.parse(path)
        
        if handler.record == None or handler.record == '':
            # failed to find what we were looking for
            print 'didnt find object we wanted'
            object = None
        else:
            print 'Now using from_xml to populate object'
            object.FromXML(object, handler.record.encode('ascii', 'replace'))
        
    else:
        print "Don't know how to load object of type", object_type
        
        
    return object


def load_item_from_working_copy(object_type, object_id, projectname, versioned):
    """ TODO: docstring """
    
    # retrieve the path for this object
    path = {
        OBJECT_TYPES.PROJECT : constants.WC_PROJECT,
        OBJECT_TYPES.ISSUE : constants.WC_ISSUES,
        OBJECT_TYPES.ISSUE_COMMENT : constants.WC_ISSUES_COMMENTS,
        OBJECT_TYPES.USER_ISSUE_STAR : constants.WC_ISSUES_USER_ISSUE_STARS,
        OBJECT_TYPES.ISSUE_USER_STAR : constants.WC_ISSUES_ISSUE_USER_STARS,
    }.get(object_type, None)
    
    
    # replace wildcards in the save path
    if(path) is not None:
        path = path \
            .replace('%projectname%', projectname) \
            .replace('%uid',str(object_id))
    else:
        raise UnsupportedArtifactException('Attempted to load an invalid artifact from working copy:' +
            '\nProject Name: ' + projectname +
            '\nArtifact type: ' + object_type +
            '\nArtifact ID: ' + str(object_id))
        
    # construct the full path
    if(versioned):
        path = os.path.join(
            constants.WORKING_DIR, constants.VERSIONED_STORAGE_ROOT, path)
    else:
        path = os.path.join(
            constants.WORKING_DIR, constants.UNVERSIONED_STORAGE_ROOT, path)
    
    if not os.path.exists(path):
        return None

    object = None
    if object_type == OBJECT_TYPES.PROJECT:
        object = demetrius_pb.Project()
#    elif object_type == OBJECT_TYPES.USER:
#        pass
    # TODO: other object types 
    
    if not object == None:
        # parse!
        handler = SingleObjectLoadSaxHandler(object_type, object_id)
        parser = make_parser()
        parser.setContentHandler(handler)
        print 'about to parse', path
        parser.parse(path)
        
        if handler.record == None or handler.record == '':
            # failed to find what we were looking for
            print 'didnt find object we wanted'
            object = None
        else:
            print 'Now using from_xml to populate object'
            object.FromXML(object, handler.record.encode('ascii', 'replace'))
        
    else:
        print "Don't know how to load object of type", object_type
        
        
    return object


def save_to_local_disk(object_type, object_id, object):
    
    # retrieve the path for this object
    save_path = {
        OBJECT_TYPES.PROJECT : constants.LD_PROJECTS,
        OBJECT_TYPES.USER : constants.LD_USERS
    }.get(object_type, None)
    
    if(save_path) is None:
        raise UnsupportedArtifactException('Attempted to save an invalid artifact to local disk:' +
            '\nArtifact type: ' + object_type +
            '\nArtifact ID: ' + str(object_id))
    
    # construct the full path
    save_path = os.path.join(
        constants.WORKING_DIR, constants.LOCAL_STORAGE_ROOT, save_path)

    _do_save(save_path, object_type, object_id, object)
    
    
def save_to_working_copy(projectname, object_type, object_id, object, versioned):
    
    # retrieve the path for this object
    save_path = {
        OBJECT_TYPES.PROJECT : constants.WC_PROJECT,
        OBJECT_TYPES.ISSUE : constants.WC_ISSUES,
        OBJECT_TYPES.ISSUE_COMMENT : constants.WC_ISSUES_COMMENTS,
        OBJECT_TYPES.USER_ISSUE_STAR : constants.WC_ISSUES_USER_ISSUE_STARS,
        OBJECT_TYPES.ISSUE_USER_STAR : constants.WC_ISSUES_ISSUE_USER_STARS,
    }.get(object_type, None)
    
    # replace wildcards in the save path
    if(save_path) is not None:
        save_path = save_path \
            .replace('%projectname%', projectname) \
            .replace('%uid',str(object_id))
    else:
        raise UnsupportedArtifactException('Attempted to save an invalid artifact to working copy:' +
            '\nProject Name: ' + projectname +
            '\nArtifact type: ' + object_type +
            '\nArtifact ID: ' + str(object_id))
        
    # construct the full path
    if(versioned):
        save_path = os.path.join(
            constants.WORKING_DIR, constants.VERSIONED_STORAGE_ROOT, save_path)
    else:
        save_path = os.path.join(
            constants.WORKING_DIR, constants.UNVERSIONED_STORAGE_ROOT, save_path)
    
    _do_save(save_path, object_type, object_id, object)
    

def _do_save(save_path, object_type, object_id, object):
    
    temp_save_path = save_path + '.tmp'
    
    # make sure that the directories exist
    try:
        os.makedirs(os.path.split(save_path)[0])
    except OSError:
        # this probably (hopefuly!) means that the directory already exists
        pass
    
    # if the file doesn't exist, create it an add it to subversion
    if not os.path.exists(save_path):
        file = open(save_path, 'w')
        file.write(object.to_pretty_xml())
        file.close()
    
    else:
        # the file does exist
        # parse through it, either replacing the given item or adding it
        
        # set up the parser
        handler = FindAndReplaceSaxHandler(temp_save_path, object_type, object_id, object)
        parser = make_parser()
        parser.setContentHandler(handler)
        
        # actually do the parsing, producing the .tmp file
        parser.parse(save_path)
        
        # if we never found the item to replace, we must do
        # a second pass and just insert the item
        if(not handler.found_target):
            handler = InsertionSaxHandler(temp_save_path, object_type, object_id, object)
            parser.setContentHandler(handler)
            parser.parse(save_path)
    
        # replace the real file with the .tmp file
        shutil.move(temp_save_path, save_path)


class SingleObjectLoadSaxHandler(ContentHandler):
    
    NEW_LINE = '\n'
    
    def __init__(self, object_type, object_id):
        """
        Retrieve the XML for a single object
        """
        
        self._object_type = object_type
        self._object_id = str(object_id)
        self._object = object
        
        self.record = '' # will be loaded with XML
        
        self._recording = False
        self._recording_tagname = ''
        
        self.found_target = False
        

    def _start_recording(self, tagname):
        """
        Begin recording xml being encountered, until the cooresponding
        end tag is encountered. For instance, if we start recording
        on a <Project> element, we will end recording on a </Project>
        element, including the start and end tag
        """
        self._recording = True
        self._recording_tagname = tagname
    
    def _make_attribute_list(self, attrs):
        attributes = ''
        for attribute in attrs.keys():
            attributes += ' ' + attribute + '="' + attrs.getValue(attribute) + '"'
        return attributes    
    
    def startElement(self, name, attrs):
        
        if name == self._object_type \
            and attrs.has_key("id") \
            and attrs.get("id") == self._object_id:
            # found the object we're looking for
               
            print 'started recording'  
                
            self._start_recording(self._object_type)
            self.found_target = True
            
        if self._recording:
            self.record += '<' \
                + name \
                + self._make_attribute_list(attrs) \
                + '>'
    
    
    def endElement(self, name):
        
        if self._recording:
            self.record += '</' \
                + name \
                + '>'
            
        # stop recording if appropriate    
        if self._recording and self._recording_tagname == name:
            self._recording = False
            # TODO: stop parsing the rest of the document, we don't need it
            # do this by raising a SAXException maybe?
        
        
    def characters(self, content):
        
        if self._recording:
        
            # we don't do anything with no content
            if content is None or content is '' or content.isspace():
                pass
            else:
                self.record += content.strip()



class FindAndReplaceSaxHandler(ContentHandler):
    
    NEW_LINE = '\n'
    
    def __init__(self, save_path, object_type, object_id, object):
        """
        Set up a new handler to perform a find and replace
        operation on an xml file, replacing the tag
        
        <object_type id="object_id">
            ...
        </object_type>
        
        with object.to_pretty_xml()
        """
        
        self._object_type = object_type
        self._object_id = str(object_id)
        self._object = object
        
        self.save_file = open(save_path, 'w')
        
        # keeping track of how many tabs to insert
        # see _do_indents()
        self.indention = 0
        
        # see _lock()
        self._locked = False
        self._locked_tagname = ''
        
        self.found_target = False
        

    def _lock(self, tagname):
        """
        Do not fire any handlers until the specified tag name's end 
        tag has been reached.
        
        For instance, calling _lock('issue') will stop handlers
        from being fired until a </issue> tag is encountered
        """
        self._locked = True
        self._locked_tagname = tagname
    
    
    def _do_indents(self):
        indents = ''
        for i in range(0,self.indention):
            indents += '  '
        return indents
    
            
    def _make_attribute_list(self, attrs):
        attributes = ''
        for attribute in attrs.keys():
            attributes += ' ' + attribute + '="' + attrs.getValue(attribute) + '"'
        return attributes
    
    
    def startElement(self, name, attrs):
        
        if not self._locked:

            if name == self._object_type \
                and attrs.has_key("id") \
                and attrs.get("id") == self._object_id:
                
                self.save_file.write(self._do_indents() 
                                     + self._object.to_pretty_xml()
                                     + self.NEW_LINE)
                self._lock(self._object_type)
                self.found_target = True
            else:
                 self.save_file.write(self._do_indents() + '<' 
                                      + name 
                                      + self._make_attribute_list(attrs) 
                                      + '>'
                                      + self.NEW_LINE)
            
            self.indention += 1
    
    
    def endElement(self, name):
        
        if not self._locked:
            self.indention -= 1
            self.save_file.write(self._do_indents() 
                                 + '</' + name + '>'
                                 + self.NEW_LINE)
            
        # unlock the handlers if appropriate    
        if self._locked and self._locked_tagname == name:
            self._locked = False
            self.indention -= 1
            
        # close the file if we've come to the end of parsing
        # TODO: there has got to be a better way to do this
        if name == 'xml':
            self.save_file.close()
        
        
    def characters(self, content):
        
        if not self._locked:
        
            # we don't do anything with no content
            if content is None or content is '' or content.isspace():
                pass
            else:
                self._do_indents()
                self.save_file.write(self._do_indents() 
                                     + content.strip()
                                     + self.NEW_LINE)


class InsertionSaxHandler(FindAndReplaceSaxHandler):
    
    def __init__(self, save_path, object_type, object_id, object):
        FindAndReplaceSaxHandler.__init__(self, save_path, object_type, object_id, object)
        self._insert_done = False
        
    def startElement(self, name, attrs):

        if not self._insert_done:
            
            if name == self._object_type:
                self.save_file.write(self.NEW_LINE
                                     + self._object.to_pretty_xml()
                                     + self.NEW_LINE
                                     + self.NEW_LINE)
                self._insert_done = True
                
                
            self.save_file.write(self._do_indents() + '<' 
                     + name 
                     + self._make_attribute_list(attrs) 
                     + '>'
                     + self.NEW_LINE)
        else:
            self.save_file.write(self._do_indents() + '<' 
                                 + name 
                                 + self._make_attribute_list(attrs) 
                                 + '>'
                                 + self.NEW_LINE)
            
            
        self.indention += 1  




class Error(Exception):
  """Base class for errors from this module."""

class UnsupportedArtifactException(Error):
  """Tried to save an unsupported object type"""





if __name__ == '__main__':
    pass
    
     
     