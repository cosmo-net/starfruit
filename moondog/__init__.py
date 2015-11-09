# -*- coding: utf-8 -*-
'''
    Starfruit stuff.
'''

# This fruit is part of starstuff.

# Distributed under the terms of the last AGPL License. 
# The full license is in the file LICENCE, distributed as part of this software.

__author__ = 'Jean Chassoul'


#import cookielib
from md5 import md5
from pprint import pprint
from urlparse import urlparse
from urlparse import urljoin
from xml.etree import ElementTree
from tornado import httpclient
from tornado import ioloop
from tornado.httputil import HTTPHeaders
from tornado.httpclient import  HTTPRequest as _HTTPRequest
from tornado.httpclient import HTTPError as _HTTPError

import logging

from starfruit import ami


class ManagerException(Exception):
    '''
        Asterisk Manager Exception.

        Base exception class
    '''
    pass


class HTTPRequest(_HTTPRequest):

    def __init__(self, url, method='GET', headers=None,
                 auth_username=None, auth_password=None,
                 connect_timeout=20.0, request_timeout=20.0,
                 allow_ipv6=False):
        '''
            HTTPRequest.

            All parameters except 'url' are optional.

            Parameters.
                - url: string URL to fetch
                - method: string 'GET' or 'POST'
                - headers: 'HTTPHeaders' or 'dict'
                - auth_username: Username for HTTP "Basic" authentication
                - auth_password: Password for HTTP "Basic" authentication
                - connect_timeout: Timeout for initial connection in seconds
                - request_timeout: Time out for entire request in seconds
                - allow_ipv6: Use IPv6 when available? Default is false
        '''
        self.url = url
        self.method = method
        self.headers = headers
        self.auth_username = auth_username
        self.auth_password = auth_password
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self.allow_ipv6 = allow_ipv6

        # parse a dictionary?
        _HTTPRequest.__init__(
            self,
            url=self.url,
            method=self.method,
            headers=self.headers,
            auth_username=self.auth_username,
            auth_password=self.auth_password,
            connect_timeout=self.connect_timeout,
            request_timeout=self.request_timeout,
            allow_ipv6=self.allow_ipv6
        )


class Manager(object):
    '''
        This class allows direct access to the Asterisk Manager Interface via HTTP.
    '''

    def __init__(self, server, username, password, prefix='', port=8088):
        '''
            Creates connection to Asterisk Manager

            All parameters except 'server', 'username' and 'password' are optional.

            TODO: parameters vs arguments?

            # explain here base on textbook.
            # bonus arity points.

            Arguments.
                - server:    <str value>
                - username:      <int value>
                - password:     <str value>
                - prefix:       <str value>
                - port:     <str value>
                - curl_httpclient:      <str value>
                - allow_ipv6:       <str value>
        '''
        
        # TODO: enable and disable simple_httpclient and curl_httpclient Async HTTP Client implementations.
        
        self.url = urlparse('http://%s:%d' % (server, port))
        self.username = username
        self.password = password
        # if prefix on the manager url
        if prefix:
            self.url = urlparse(urljoin(self.url.geturl(), prefix))
        
        # Non-blocking CURL HTTP client. (Default False)
        
        # Note that if you are using curl_httpclient, it is highly recommended
        # that you use a recent version of libcurl and pycurl.
        
        self.curl_httpclient = False
        # Support for (IPv6) Internet Protocol version 6. (Default False)
        self.allow_ipv6 = False
        # get the asterisk version
        self.asterisk_version = None
        # Tornado httpclient
        # TODO: change the HTTP client method
        httpclient.AsyncHTTPClient.configure(
            "tornado.curl_httpclient.CurlAsyncHTTPClient"
        )

        self.http_client = httpclient.AsyncHTTPClient()

        # TODO: get the connection cookie!!!

        # EXPERIMENTAL SHITS AND STUFF

        # TODO: session shits and stuff
        self._session_id = None

        # Boom, boom, boom!

        # da fuq... nonce, cnonce and nc
        self.server_nonce = None
        self.client_nonce = None
        self.nonce_count = '00000000'

        # TODO: and ioloop per instance?
        self._ioloop = ioloop.IOLoop.instance()

    def _handle_request(self, response):
        # TODO: refactor this method, maybe is better to implement a handler class. <-- class of objects for hooks

        if response.code == 401:
            # build the authorization headers
            authorization = None
            # da fuq is digest_response ???
            digest_respose = None

            # headers from the server response
            headers  = response.headers
            headers = [headers[k] for k in headers if k == 'Www-Authenticate']

            if headers:
                headers = headers[0].replace('"', '')
                headers = dict(item.split('=') for item in headers.split(', '))

                # set the realm
                self.realm = headers['realm']

                # TODO: test the server nonce implementation
                # TODO: I need to restart the nc when a new server_nonce is set from this method
                # set the server nonce
                self.server_nonce = headers['nonce']

                # Response request
                request = response.request

                # Digest auth HA1
                ha1 = md5(':'.join((self.username, self.realm, self.password))).hexdigest()
                # Digest auth HA2
                ha2 = md5(':'.join((request.method, request.url))).hexdigest()

                # TODO: i need to check the nounce count
                nc = self.nonce_count
                # TODO: i need to check the client nonce
                cnonce = self.client_nonce
                # Auth Digest response, please work motherfucker!!
                digest_response = md5(':'.join((ha1, headers['nonce'], nc, cnonce, headers['qop'], ha2))).hexdigest()

                xxx = urlparse(request.url)

                # build the authorization header
                authorization = 'Digest username="%s", '\
                                'realm="%s", '\
                                'nonce="%s", '\
                                'uri="%s", '\
                                'algorithm=MD5, '\
                                'response="%s", '\
                                'opaque="%s", '\
                                'qop=%s, '\
                                'nc=%s, '\
                                'cnonce="%s"' \
                    % (self.username,
                       self.realm,
                       headers['nonce'],
                       xxx.path,
                       digest_response,
                       headers['opaque'],
                       headers['qop'],
                       nc,
                       cnounce
                       )

            # let the authorization test begings
            print authorization

            # headers from the client request
            # response.request.headers
            h = HTTPHeaders({'Authorization': authorization})

            request = response.request
            request.headers = h

            self.http_client.fetch(request, self._handle_request)
            
            #response.request.headers = h
            #request = response.request

            print(self.url)

        if response.error:
            logging.error(u'error', response.error)
        else:
            print(response.body)
            pprint(response.headers)
            pprint(response.request.headers)


        # Stop the ioloop instance??? really?
        ioloop.IOLoop.instance().stop()


    def query(self, action, **kwargs):
        '''
            - /amanager: HTML Manager Event Interface w/Digest authentication
            - /arawman: Raw HTTP Manager Event Interface w/Digest authentication
            - /amxml: XML Manager Event Interface w/Digest authentication
        '''
        # action args
        action_args = '&'.join("%s=%s" % (key, kwargs[key]) for key in kwargs)

        request_url = urljoin(
            self.url.geturl(),
            "%s/amxml?action=%s&%s" % (self.url.path, action, action_args)
        )

        '''

        # this looks like a jinja template

        url: string URL to fetch
            - auth_username: Username for HTTP "Basic" authentication
            - auth_password: Password for HTTP "Basic" authentication
            - connect_timeout: Timeout for initial connection in seconds
            - request_timeout: Time out for entire request in seconds
            - allow_ipv6

        '''

        headers = HTTPHeaders()

        # TODO: The IPv6 stuff and shits
        request = HTTPRequest(
            url=request_url,
            auth_username=self.username,
            auth_password=self.password,
            headers=headers,
            allow_ipv6=self.allow_ipv6
        )

        self.http_client.fetch(request, self._handle_request)

        # Manager ioloop instance
        self._ioloop.start()

    def login(self):
        '''
            Login the manager.
        '''
        self.query('login', username=self.username, secret=self.password)

    def logout(self):
        '''
            Logout the manager.
        '''
        self.query('logout')

if __name__ == '__main__':
    AMI = Manager('192.168.13.52', 'ooo', '1234')
    #AMI.login()
    AMI.logout()
    print('Thanks for all the stuff.')
