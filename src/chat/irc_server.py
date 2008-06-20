#! /usr/bin/env python

from time import ctime

from twisted import copyright

from twisted.python import failure

from twisted.internet import reactor, defer

from twisted.cred import checkers, portal, credentials
from twisted.cred import credentials, error as crederror
from twisted.cred.checkers import ICredentialsChecker

from twisted import words
from twisted.words import iwords, ewords
from twisted.words.service import InMemoryWordsRealm, IRCFactory, IRCUser, Group
from twisted.words.protocols import irc

from zope.interface import implements


NICKSERV = 'NickServ!NickServ@services'
class LonghouseIRCServer ( IRCUser ):
        
    def connectionMade(self):
        self.irc_PRIVMSG = self.irc_NICKSERV_PRIVMSG  
        
    def irc_NICK(self, prefix, params):
        
        try:
            self.logout()
        except:
            pass
        
        try:
            nickname = params[0].decode(self.encoding)
        except UnicodeDecodeError:
            self.privmsg(
                NICKSERV,
                nickname,
                'Your nickname is cannot be decoded.  Please use ASCII or UTF-8.')
            self.transport.loseConnection()
            return
        
        if self.password is None:
            self.password = ''
        
        password = self.password
        
        self.password = None
        self.logInAs(nickname, password)
        pass
        

    def _cbLogin(self, (iface, avatar, logout)):
        """Had to be overridden from the superclass because of a bug."""
        
        assert iface is iwords.IUser, "Realm is buggy, got %r" % (iface,)

        # Let them send messages to the world
        try:
            del self.irc_PRIVMSG
        except AttributeError:
            # they were signed in before
            pass

        self.avatar = avatar
        self.logout = logout
        self.realm = avatar.realm
        self.hostname = self.realm.name

        info = {
            "serviceName": self.hostname,
            "serviceVersion": copyright.version,
            "creationDate": ctime(), # XXX
            }
        for code, text in self._welcomeMessages:
            self.sendMessage(code, text % info)


    def _ebLogin(self, err, nickname):
        if err.check(ewords.AlreadyLoggedIn):
            self.privmsg(
                NICKSERV,
                nickname,
                "%s is already logged in.")
        elif err.check(crederror.UnauthorizedLogin):
            self.privmsg(
                NICKSERV,
                nickname,
                "Login failed.")
        else:
            #log.msg("Unhandled error during login:")
            #log.err(err)
            print "Unhandled error during login:"
            print err
            self.privmsg(
                NICKSERV,
                nickname,
                "Server error during login.")
        #self.transport.loseConnection()


class LonghouseIRCFactory( IRCFactory ):
    protocol = LonghouseIRCServer       

def getLonghouseIRCFactory():
    realm = LonghouseIRCRealm('longhouse_irc')
    checker = LonghouseCredChecker()
    p = portal.Portal(realm, [checker])
    
    factory = LonghouseIRCFactory(realm, p)
    return factory
    

class LonghouseCredChecker:
    implements(ICredentialsChecker)

    credentialInterfaces = (credentials.IUsernamePassword,
                            credentials.IUsernameHashedPassword)

    def __init__(self, **users):
        self.users = users

    def addUser(self, username, password):
        self.users[username] = password

    def _cbPasswordMatch(self, matched, username):
        if matched:
            return username
        else:
            return failure.Failure(crederror.UnauthorizedLogin())

    def requestAvatarId(self, credentials):
        #if credentials.username in self.users:
        #    print 'checking creds:', dir(credentials)
        #    print credentials.username, credentials.password
        #    return defer.maybeDeferred(
        #        credentials.checkPassword,
        #        self.users[credentials.username]).addCallback(
        #        self._cbPasswordMatch, str(credentials.username))
        #else:
        #    #return defer.fail(error.UnauthorizedLogin())
        #    self.addUser(credentials.username, 'changeme')
        #    return credentials.username
        return credentials.username



class LonghouseIRCRealm( InMemoryWordsRealm ):

    def __init__(self, *a, **kw):
        super(LonghouseIRCRealm, self).__init__(*a, **kw)
        self.createGroupOnRequest = True
    
    def groupFactory(self, name):
        group = Group(name)
        self.groups[name] = group
        return group


if __name__ == '__main__':
    print 'blah'
    #import sys, os
    #
    #realm = LonghouseIRCRealm('longhouse_irc')
    #checker = LonghouseCredChecker()
    #
    #portal = portal.Portal(realm, [checker])
    #
    #factory = LonghouseIRCFactory(realm, portal)
    #
    #reactor.listenTCP(6667, factory)
    #reactor.run()
