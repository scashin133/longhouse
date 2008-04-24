# -*- test-case-name: twisted.words.test.test_jabbersaslmechanisms -*-
#
# Copyright (c) 2001-2006 Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Protocol agnostic implementations of SASL authentication mechanisms.
"""

import md5, binascii, random, time, os

from zope.interface import Interface, Attribute, implements

class ISASLMechanism(Interface):
    name = Attribute("""Common name for the SASL Mechanism.""")

    def getInitialResponse():
        """
        Get the initial client response, if defined for this mechanism.

        @return: initial client response string.
        @rtype: L{str}.
        """


    def getResponse(challenge):
        """
        Get the response to a server challenge.

        @param challenge: server challenge.
        @type challenge: L{str}.
        @return: client response.
        @rtype: L{str}.
        """



class Plain(object):
    """
    Implements the PLAIN SASL authentication mechanism.

    The PLAIN SASL authentication mechanism is defined in RFC 2595.
    """
    implements(ISASLMechanism)

    name = 'PLAIN'

    def __init__(self, authzid, authcid, password):
        self.authzid = authzid or ''
        self.authcid = authcid or ''
        self.password = password or ''


    def getInitialResponse(self):
        return "%s\x00%s\x00%s" % (self.authzid.encode('utf-8'),
                                   self.authcid.encode('utf-8'),
                                   self.password.encode('utf-8'))



class DigestMD5(object):
    """
    Implements the DIGEST-MD5 SASL authentication mechanism.

    The DIGEST-MD5 SASL authentication mechanism is defined in RFC 2831.
    """
    implements(ISASLMechanism)

    name = 'DIGEST-MD5'

    def __init__(self, serv_type, host, serv_name, username, password):
        self.username = username
        self.password = password
        self.defaultRealm = host

        self.digest_uri = '%s/%s' % (serv_type, host)
        if serv_name is not None:
            self.digest_uri += '/%s' % serv_name


    def getInitialResponse(self):
        return None


    def getResponse(self, challenge):
        directives = self._parse(challenge)

        # Compat for implementations that do not send this along with
        # a succesful authentication.
        if directives.has_key('rspauth'):
            return ''

        try:
            realm = directives['realm']
        except KeyError:
            realm = self.defaultRealm

        return self._gen_response(directives['charset'],
                                  realm,
                                  directives['nonce'])

    def _parse(self, challenge):
        """
        Parses the server challenge.

        Splits the challenge into a dictionary of directives with values.

        @return: challenge directives and their values.
        @rtype: L{dict} of L{str} to L{str}.
        """
        directive_list = challenge.split(',')
        directives = {}
        for directive in directive_list:
            name, value = directive.split('=')
            value = value.replace("'","")
            value = value.replace('"','')
            directives[name] = value
        return directives


    def _unparse(self, directives):
        """
        Create message string from directives.

        @param directives: dictionary of directives (names to their values).
                           For certain directives, extra quotes are added, as
                           needed.
        @type directives: L{dict} of L{str} to L{str}
        @return: message string.
        @rtype: L{str}.
        """

        directive_list = []
        for name, value in directives.iteritems():
            if name in ('username', 'realm', 'cnonce',
                        'nonce', 'digest-uri', 'authzid'):
                directive = '%s="%s"' % (name, value)
            else:
                directive = '%s=%s' % (name, value)

            directive_list.append(directive)

        return ','.join(directive_list)


    def _gen_response(self, charset, realm, nonce):
        """
        Generate response-value.

        Creates a response to a challenge according to section 2.1.2.1 of
        RFC 2831 using the L{charset}, L{realm} and L{nonce} directives
        from the challenge.
        """

        def H(s):
            return md5.new(s).digest()

        def HEX(n):
            return binascii.b2a_hex(n)

        def KD(k, s):
            return H('%s:%s' % (k, s))

        try:
            username = self.username.encode(charset)
            password = self.password.encode(charset)
        except UnicodeError:
            # TODO - add error checking
            raise

        nc = '%08x' % 1 # TODO: support subsequent auth.
        cnonce = self._gen_nonce()
        qop = 'auth'

        # TODO - add support for authzid
        a1 = "%s:%s:%s" % (H("%s:%s:%s" % (username, realm, password)),
                           nonce,
                           cnonce)
        a2 = "AUTHENTICATE:%s" % self.digest_uri

        response = HEX( KD ( HEX(H(a1)),
                             "%s:%s:%s:%s:%s" % (nonce, nc,
                                                 cnonce, "auth", HEX(H(a2)))))

        directives = {'username': username,
                      'realm' : realm,
                      'nonce' : nonce,
                      'cnonce' : cnonce,
                      'nc' : nc,
                      'qop' : qop,
                      'digest-uri': self.digest_uri,
                      'response': response,
                      'charset': charset}

        return self._unparse(directives)


    def _gen_nonce(self):
        return md5.new("%s:%s:%s" % (str(random.random()) , str(time.gmtime()),str(os.getpid()))).hexdigest()
