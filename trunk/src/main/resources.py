import sys, re

import twisted.internet.utils
from twisted.internet import threads, reactor, defer

from twisted.web import resource, static
from twisted.web import server
from twisted.python import log

from common import ezt_google


class BadRequestError(Exception):
    """The request was invalid"""


class HandlerResource(resource.Resource):
    """Wrapper for a handler method, allowing it to be treated as
    a Twisted resource"""  
    
    ifLeaf = True
    
    def __init__(self, handler):
        resource.Resource.__init__(self)
        self.handler = handler
       
    def getChildWithDefault(self, path, request):
        """There are never any children, always return self"""
        return self       
       
    def render_GET(self, request):
        """Call the handler method"""
        
        #print 'blockingCallFromThread in render_GET'
        ##result = threads.deferToThread( threads.blockingCallFromThread(reactor, self.blocker) )
        #result = threads.blockingCallFromThread(reactor, self.getEchoOutput)
        #print result
        #print 'done with blocking call'
        
        try:
            handler_result = self.handler(request)

            # TODO: use isinstance() here instead?
            if str(handler_result.__class__) == 'twisted.internet.defer.Deferred':
                # handler resulted in a deferred, we'll wait until it's done to finish the request
                print 'handler was a deferred! adding callback to respond'
                
                def respond(data):
                    print 'finally responding to deferred handler with:', data
                    #request.write(str(data))
                    request.finish()
                    
                handler_result.addCallback(respond)
            else:
                # handler is not deferred, we assume it's done now and we can finish the request
                #request.write('?')    
                print 'handler was not a deferred, it was a', str(handler_result.__class__)
                print 'finishing request now'
                request.finish();

        except Exception, e:
            print 'exception in HandlerResource.render_GET:', e
            raise e

        return server.NOT_DONE_YET


#   def _respond(self, data):
#       print 'finally responding to deferred handler with:', data
#       self.request.write(str(data))
#       self.request.finish()
        
        
        
        request.finish()   
        return server.NOT_DONE_YET     
        
    render_POST = render_GET
    
    def getEchoOutput(self):
        args = ['hello!']
        return twisted.internet.utils.getProcessOutputAndValue(
                    '/bin/echo', args)
        
    def blocker(self):
        d = defer.Deferred()
        seconds = 3
        outval = '42'
        print "- main thread has made a Deferred. will call back in %d seconds." % seconds
        def blockerdone():
            print "- %d seconds done. Now callback-ing Deferred with %r." % (seconds, outval)
            d.callback(outval)
        reactor.callLater(seconds, blockerdone)
        print "- blocker is done and is returning the Deferred."
        return d
    
class DeferredHandlerResource(resource.Resource):
    """Wrapper for a deferred handler method."""
    
    isLeaf = True
    
    def __init__(self, handler):
        resource.Resource.__init__(self)
        self.handler = handler
        
    def getChildWithDefault(self, path, request):
        """There are never any children, always return self"""
        return self   
    
    def render_GET(self, request):
        """Call the handler method"""
        self.request = request
        
        d = self.handler(request)
        
        # TODO: use isinstance() here instead?
        if str(d.__class__) == 'twisted.internet.defer.Deferred':
            d.addCallback(self._respond)
        else:
            request.write('Error: Deferred handler must return \
            twisted.internet.defer.Deferred.<br> \
            Returned ' + str(d.__class__) + ' instead.')    
            request.finish();
        
        return server.NOT_DONE_YET
        
    def _respond(self, data):
        self.request.write(str(data))
        self.request.finish()
        
    render_POST = render_GET


class RootResource(resource.Resource):

    _project_handler_pattern = re.compile('/p/.*?(/.*)') # /p/projectname/foo
    _project_root_handler_pattern = re.compile('/p/.+') # /p/projectname
    
    _user_handler_pattern = re.compile('/u/.*?(/.*)') # /u/username/foo
    _user_root_handler_pattern = re.compile('/u/.+') # /u/username/foo
    
    def __init__(self):
        resource.Resource.__init__(self)
        self.handlers = {}
        self.project_handlers = {}
        self.user_handlers = {}
    
        self.handlers['404'] = HandlerResource(self._404_Handler)
    
    def getChild(self, path, request):
        """Failed to look up resource in static resources. It must be
        a dynamic resource (handler) or a bad request. Try to find the
        correct handler and return it."""
        
        try:
            if request.path.startswith('/p/'):
                m = re.match(self._project_handler_pattern, request.path)
                if m:
                    return self.project_handlers[m.group(1)]
                else:
                    m = re.match(self._project_root_handler_pattern, request.path)
                    if m:
                        return self.project_handlers['/']
                    else:
                        raise BadRequestError()
            elif request.path.startswith('/u/'):
                m = re.match(self._user_handler_pattern, request.path)
                if m:
                    return self.user_handlers[m.group(1)]
                else:
                    m = re.match(self._user_root_handler_pattern, request.path)
                    if m:
                        return self.user_handlers['/']
                    else:
                        raise BadRequestError()
            else:
                return self.handlers[request.path]
        except (KeyError, BadRequestError):
            return self.handlers['404']

   
    def addHandler(self, path, handler):
        """Wrap the handler with a HandlerResource and add it
        to the dictionary of handlers"""
        print 'adding handler to path', path
        self.handlers[path] = HandlerResource(handler)

    def addProjectHandler(self, path, handler):
        print 'adding project handler to path', path
        self.project_handlers[path] = HandlerResource(handler)
        
    def addUserHandler(self, path, handler):
        print 'adding user handler to path', path
        self.user_handlers[path] = HandlerResource(handler)
        
    def addDeferredHandler(self, path, handler):
        """Wrap the handler with a DeferredHandlerResource
        (expects a deferred as the return type)"""
        self.handlers[path] = DeferredHandlerResource(handler)

    def addProjectDeferredHandler(self, path, handler):
        self.project_handlers[path] = DeferredHandlerResource(handler)    
        
    def _404_Handler(self, request):
        template = ezt_google.GoogleTemplate('templates/framework/404.ezt')
        template.WriteResponse(request, {})
        
        