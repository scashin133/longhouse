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

"""Unit tests for Demetrius RequestInfo class.
"""

import unittest
import threading
import time
import sys
import traceback
import re

from twisted.web import server, client
from twisted.internet import reactor

from main import resources
from framework import requestinfo

class MockURL(object):
    def __init__(self, params_dict):
        self.params = params_dict

    def GetQueryComponent(self, query_param_name):
        """Pretend to parse query param from URL"""
        return self.params.get(query_param_name, None)

class RequestInfoParamSlice(requestinfo.RequestInfo):
    """Subclass of RequestInfo for testing that focuses only on params."""

    def __init__(self, synthetic_params, url):
        self.synthetic_params = synthetic_params
        self.url = url
        # Note: we do not call RequestInfo.__init__()


class SandboxServer(threading.Thread):
    
    def __init__(self, serviceport, fail_callback):
        
        self.port = serviceport
        self.fail_callback = fail_callback
        
        # register resources
        self.root_resource = resources.HandlerResource()
        
        # set up web server
        self.site = server.Site(self.root_resource)

        # init superclass (Thread)
        threading.Thread.__init__(self)

    def run(self):
        reactor.listenTCP(self.port, self.site)
        reactor.run(installSignalHandlers=0)
        
    def stop(self):
        reactor.removeAll()
        reactor.stop()
        

    def RegisterHandler(self, relative_uri, callback, private=False,
                                    does_write=None):
        self.root_resource.handlers[relative_uri] = callback 

class Failer:
    def __init__(self):
        self.traceback = None
        
    def fail(self, traceback):
        if self.traceback == None:
            self.traceback = traceback
        else:
            # we only want to record the traceback for the first failure
            pass
        
    def has_failed(self):
        return not self.traceback == None

    def get_traceback(self):
        return self.traceback
    
    def reset(self):
        self.traceback = None

class RequestInfoUnitTest(unittest.TestCase):

    failer = Failer()
    sandboxserver = SandboxServer(8079, failer)
    sandboxserver.start()
    
    def setUp(self):
        self.failer.reset()
            
    def tearDown(self):
        pass

    def testGetIntListParamNoParam(self):
        ri = RequestInfoParamSlice({}, MockURL({}))
        self.assertEquals(ri.GetIntListParam('ids'), None)
        self.assertEquals(ri.GetIntListParam('ids', default_value=['test']),
                      ['test'])
    
    def testGetIntListParamOneValue(self):
        ri = RequestInfoParamSlice({}, MockURL({'ids': '11'}))
        self.assertEquals(ri.GetIntListParam('ids'), [11])
        self.assertEquals(ri.GetIntListParam('ids', default_value=['test']),
                      [11])

    def testGetIntListParamMultiValue(self):
        ri = RequestInfoParamSlice({}, MockURL({'ids': '21,22,23'}))
        self.assertEquals(ri.GetIntListParam('ids'), [21,22,23])
        self.assertEquals(ri.GetIntListParam('ids', default_value=['test']),
                      [21, 22, 23])

    def testGetIntListParamBogusValue(self):
        ri = RequestInfoParamSlice({}, MockURL({'ids': 'foo'}))
        self.assertEquals(ri.GetIntListParam('ids'), None)
        self.assertEquals(ri.GetIntListParam('ids', default_value=['test']),
                      ['test'])

    def testGetIntListParamMalformed(self):
        ri = RequestInfoParamSlice({}, MockURL({'ids': '31,32,,'}))
        self.assertEquals(ri.GetIntListParam('ids'), None)
        self.assertEquals(ri.GetIntListParam('ids', default_value=['test']),
                      ['test'])

    def testGetIntListParamFromSyntheticOnly(self):
        ri = RequestInfoParamSlice({'ids': [41, 42]}, MockURL({}))
        self.assertEquals(ri.GetIntListParam('ids'), [41, 42])
        self.assertEquals(ri.GetIntListParam('ids', default_value=['test']),
                      [41, 42])

    def testGetIntListParamFromSyntheticFirst(self):
        ri = RequestInfoParamSlice({'ids': [51, 52]},
                               MockURL({'ids': '58,59'}))
        self.assertEquals(ri.GetIntListParam('ids'), [51,52])
        self.assertEquals(ri.GetIntListParam('ids', default_value=['test']),
                      [51,52])


    def testParseURI(self):
        # TODO: why do we get a warning about request.finish() being called twice?
        
        def Handler(request):
            req_info = requestinfo.RequestInfo()
            try:
                req_info.ParseURI(request)
                
                # was the url parsed correctly?
                expected = 'http://localhost:8079/test'
                if not req_info.current_page_url == expected:
                    self.failer.fail('wrong current_page_url. got ' + req_info.current_page_url + ", expected " + expected)
                
                # was the url encoded correctly?
                expected_encoded = 'http%3A%2F%2Flocalhost%3A8079%2Ftest'
                if not req_info.current_page_url_encoded == expected_encoded:
                    self.failer.fail('wrongly encoded url. got ' + req_info.current_page_url_encoded + ", expected " + expected_encoded)
                    
            except Exception:
                self.failer.fail(traceback.format_exc())
        
        self.sandboxserver.RegisterHandler('/test', Handler)

        page = client.getPage("http://localhost:8079/test?foo=bar")  
        time.sleep(3)
        
        if self.failer.has_failed():
            raise Exception(self.failer.get_traceback())



    def testExtractCommonParameters(self):
        
        def Handler(request):
            req_info = requestinfo.RequestInfo()
            try:
                req_info.ParseURI(request)
                req_info.ExtractCommonParameters(request, None, None)
            except Exception:
                self.failer.fail(traceback.format_exc())
        
        self.sandboxserver.RegisterHandler('/test', Handler)

        page = client.getPage("http://localhost:8079/test")  
        time.sleep(3)
        
        if self.failer.has_failed():
            raise Exception(self.failer.get_traceback())



    def testParseUserInfo(self):
        
        def Handler(request):
            req_info = requestinfo.RequestInfo()
            try:
                req_info.ParseURI(request)
                req_info.ExtractCommonParameters(request, None, None)
                req_info.ParseUserInfo(request, None, None, None)
            except Exception:
                self.failer.fail(traceback.format_exc())
        
        self.sandboxserver.RegisterHandler('/test', Handler)

        page = client.getPage("http://localhost:8079/test?a=b")  
        time.sleep(3)
        
        if self.failer.has_failed():
            raise Exception(self.failer.get_traceback())


# TODO: write tests for ParseURI, ExtractCommonParameters, ParseUserInfo

if __name__ == '__main__':
    unittest.main()
