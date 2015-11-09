# -*- coding: utf-8 -*-
'''
    Starfruit

    Communication carambolas
'''

# This file is part of starfruit.

# Distributed under the terms of the last AGPL License.
# The full license is in the file LICENCE, distributed as part of this software.

__author__ = 'Jean Chassoul'

# note this project is inspired both in pyst and obelus.
import time
import zmq
import sys
import uuid
import itertools
import socket
import logging

import motor
import queries
import pylibmc as mc

# system periodic cast callback
from tornado.ioloop import PeriodicCallback as PeriodicCast

from tornado import gen
from tornado import web

# from tornado import websocket

from starfruit.tools.adapter import TornadoAdapter, StarFruitProtocol

#from starfruit.system import records as record_tools # WTF? kind of important and shit ...
# maybe think on a better name?

from starfruit.tools import options
from starfruit.tools import indexes
from starfruit.tools import periodic

from starfruit.tools import new_resource, zmq_external_logger, create_parser, parse_args

from starfruit.handlers import CarambolaHandler

from starfruit.handlers import asterisks

from zmq.eventloop import ioloop

from tornado.iostream import IOStream


# ioloop
ioloop.install()

# iofun testing box
iofun = []

# e_tag
e_tag = False

# db global variable
db = False

# sql global variable
sql = False

# kvalue global variable
kvalue = False

# cache glogbal variable
cache = False

# external logger handler
logger = False


@gen.coroutine
def periodic_get_records():
    '''
        periodic_get_records callback function
    '''
    start = time.time()
    #recs = record_tools.Records()
    raw_records = yield [
        #periodic.get_raw_records(sql, 888),
        #periodic.get_query_records(sql, 1000),

        #periodic.process_assigned_false(db),
        #periodic.process_assigned_records(db),
    ]
    
    if all(record is None for record in raw_records):
        results = None
    else:
        results = list(itertools.chain.from_iterable(raw_records))

        for stuff in results:

            logging.error(stuff)

            #record = yield recs.new_detail_record(stuff, db)

            #checked = yield periodic.checked_flag(sql, record.get('uniqueid'))

            #flag = yield periodic.assign_record(
            #    db,
            #    stuff.get('account'),
            #    stuff.get('uuid')
            #)

            # check new resource
            #resource = yield new_resource(db, stuff, 'records')
            # check this stuff up

    end = time.time()
    periodic_take = (end - start)

    logging.info('it takes {0} processing periodic {1}'.format(
        periodic_take,
        'casts for asterisk resources'
    ))




def main():
    '''
        Starfruit communication carambolas.
    '''
    log = logging.getLogger(__name__)
    # daemon options
    opts = options.options()
    # Come on dude, grow this fruit up
    parser = create_parser(
        description="Tornado-based AMI starfruit client")
    # more options base on argument parser
    more_options, args = parse_args(parser)

    # Set document database
    document = motor.MotorClient(opts.mongo_host, opts.mongo_port).starfruit

    # Set memcached backend
    memcache = mc.Client(
        [opts.memcached_host],
        binary=opts.memcached_binary,
        behaviors={
            "tcp_nodelay": opts.memcached_tcp_nodelay,
            "ketama": opts.memcached_ketama
        }
    )

    # Set SQL URI
    postgresql_uri = queries.uri(
        host=opts.sql_host,
        port=opts.sql_port,
        dbname=opts.sql_database,
        user=opts.sql_user,
        password=None
    )

    # Set kvalue database
    global kvalue
    kvalue = kvalue

    # Set default cache
    global cache
    cache = memcache

    # Set SQL session
    global sql
    sql = queries.TornadoSession(uri=postgresql_uri)

    # Set default database
    global db
    db = document
    
    system_uuid = uuid.uuid4()
    # logging system spawned
    logging.info('Starfruit system {0} spawned'.format(system_uuid))

    # logging database hosts
    logging.info('MongoDB server: {0}:{1}'.format(opts.mongo_host, opts.mongo_port))
    logging.info('PostgreSQL server: {0}:{1}'.format(opts.sql_host, opts.sql_port))

    # Ensure 
    if opts.ensure_indexes:
        logging.info('Ensuring indexes...')
        indexes.ensure_indexes(db)
        logging.info('DONE.')

    # base url
    base_url = opts.base_url

    # system cache
    cache_enabled = opts.cache_enabled
    if cache_enabled:
        logging.info('Memcached server: {0}:{1}'.format(opts.memcached_host, opts.memcached_port))

    external_log = opts.external_log
    if external_log:
        global logger
        logger = zmq_external_logger()

    # starfruit web application daemon
    application = web.Application(

        [
            # Starfruit system knowledge (quotes) <-- on realtime events.
            (r'/system/?', CarambolaHandler),

            # Asterisks
            (r'/asterisks/(?P<asterisk_uuid>.+)/?', asterisks.Handler),
            (r'/asterisks/?', asterisks.Handler),
        ],

        # system database
        db=db,

        # system cache
        cache=cache,

        # cache enabled flag
        cache_enabled=cache_enabled,

        # document datastorage
        document=document,

        # kvalue datastorage
        kvalue=kvalue,

        # sql datastorage
        sql=sql,

        # debug mode
        debug=opts.debug,

        # application domain
        domain=opts.domain,

        # application timezone
        timezone=opts.timezone,

        # pagination page size
        page_size=opts.page_size,

        # cookie settings
        cookie_secret=opts.cookie_secret,

        # login url
        login_url='/login/'
    )

    # Starfruit periodic cast callbacks
    #periodic_records = PeriodicCast(periodic_get_records, 5000)
    #periodic_records.start()

    # Setting up starfruit HTTP listener
    application.listen(opts.port)
    logging.info('Listening on http://%s:%s' % (opts.host, opts.port))
    
    loop = ioloop.IOLoop.instance()

    # Setting up starfruit protocol listener
    
    proto = StarFruitProtocol(loop, more_options)

    adapter = TornadoAdapter(proto)
    logging.info('Listening starfruit on tcp://%s:%s' % (opts.host, opts.port))
    stream = IOStream(socket.socket(), loop)
    stream.connect((more_options.host, more_options.port),
                   lambda: adapter.bind_stream(stream))

    try:
        loop.start()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()