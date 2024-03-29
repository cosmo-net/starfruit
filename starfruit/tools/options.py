# -*- coding: utf-8 -*-
'''
    Starfruit daemon configuration options.
'''

# This file is part of starfruit.

# Distributed under the terms of the last AGPL License. 
# The full license is in the file LICENCE, distributed as part of this software.

__author__ = 'Jean Chassoul'


import os
import base64
import uuid

import tornado.options

from tornado.options import parse_config_file


#secret = base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
secret = base64.b64encode("I've said before that I'm a remarkably unsentimental monkey.")
config_path = 'starfruit.conf'

def options():
    '''
        Starfruit configuration options
    '''
    # Ensure database indexes
    tornado.options.define(
        'ensure_indexes',
        default=True,
        type=bool,
        help=('Ensure collection indexes before starting')
    )

    # Set config and stuff
    tornado.options.define(
        'config',
        type=str,
        help='path to config file',
        callback=lambda path: parse_config_file(path, final=False)
    )

    # debugging
    tornado.options.define('debug', default=False, type=bool, help=(
         'Turn on autoreload and log to stderr only'))

    # logging dir
    tornado.options.define('logdir', type=str, default='log', help=(
         'Location of logging (if debug mode is off)'))

    # Application domain
    tornado.options.define('domain', default='iofun.io', type=str,
                            help=('Application domain, e.g. "example.com"')
    )

    tornado.options.define('ami_secret', default='Cc0d3Mmach1n3Mmanager', type=str,
                            help=('AMI secret')
    )
    tornado.options.define('ami_user', default='c0d3manag3r', type=str,
                            help=('AMI username')
    )
    tornado.options.define('ami_host', default='sip.codemachine.io', type=str,
                            help=('AMI hostname')
    )
    tornado.options.define('ami_port', default=7542, type=int,
                            help=('AMI TCP port')
    )

    # Server settings
    tornado.options.define('host', default='127.0.0.1', type=str,
                           help=('Server hostname'))
    tornado.options.define('port', default=3888, type=int,
                           help=('Server port'))
    
    # MongoDB database settings
    tornado.options.define('mongo_host', type=str,
                            help=('MongoDB hostname or ip address'))

    tornado.options.define('mongo_port', default=27017, type=int,
                            help=('MongoDB port'))

    # PostgreSQL database settings
    tornado.options.define('sql_host', type=str,
                            help=('PostgreSQL hostname or ip address'))

    tornado.options.define('sql_port', default=5432, type=int,
                            help=('PostgreSQL port'))

    tornado.options.define('sql_database', type=str,
                            help=('PostgreSQL database'))

    tornado.options.define('sql_user', type=str,
                            help=('PostgreSQL username'))

    tornado.options.define('sql_password', type=str,
                            help=('PostgreSQL username password'))

    # Memcached cache datastorage settings
    tornado.options.define('memcached_host',
        default='127.0.0.1', type=str,
        help=('Memcached host'))

    # ZMQ external PUB logger
    tornado.options.define('external_log',
        default=False, type=bool,
        help=('External logger'))

    tornado.options.define('memcached_port',
        default=11211, type=int,
        help=('Memcached port'))

    tornado.options.define('memcached_binary',
        default=True, type=bool,
        help=('Memcached binary'))

    tornado.options.define('memcached_tcp_nodelay',
        default=True, type=bool,
        help=('Memcached tcp_nodelay'))

    tornado.options.define('memcached_ketama',
        default=True, type=bool,
        help=('Memcached ketama'))

    tornado.options.define('cache_enabled',
        default=False, type=bool,
        help=('Enable cache'))
    
    # Base url and timezone
    tornado.options.define('base_url', default='api', type=str,
                           help=('Base url, e.g. "api"'))
    tornado.options.define('timezone', type=str, default='America/Costa_Rica',
                           help=('Timezone'))

    # Requests with return settings
    # Pagination - Requests that return multiple items will be paginated
    # to 30 items by default.
    tornado.options.define('page_size', default=30, type=int,
                           help=('Set a custom page size up to 100'))
    tornado.options.define('cookie_secret', default=secret, type=str,
                           help=('Secure cookie secret string'))

    # Parse config file, then command line, so command line switches take
    # precedence
    if os.path.exists(config_path):
        print('Loading %s' % (config_path))

        tornado.options.parse_config_file(config_path)
    else:
        print('No config file at %s' % (config_path))
               
    tornado.options.parse_command_line()
    result = tornado.options.options

    for required in (
        'domain', 'host', 'port', 'timezone', 'base_url',
    ):
        if not result[required]:
            raise Exception('%s required' % required)

    return result