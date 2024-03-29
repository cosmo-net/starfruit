# -*- coding: utf-8 -*-
'''
    Starfruit tools system logic functions.
'''

# This file is part of starfruit.

# Distributed under the terms of the last AGPL License. 
# The full license is in the file LICENCE, distributed as part of this software.

__author__ = 'Jean Chassoul'


import sys
import time
import arrow
import datetime
import ujson as json
import motor
import argparse
import logging

from tornado import gen

from starfruit.tools.adapter import CLIOptions

from starfruit import errors

from starfruit.messages import asterisks

import zmq

from zmq.log.handlers import PUBHandler


@gen.coroutine
def check_json(struct):
    '''
        Check for malformed JSON
    '''
    try:
        struct = json.loads(struct)
    except Exception, e:
        api_error = errors.Error(e)
        error = api_error.json()

        logging.exception(e)
        raise gen.Return(error)

        return

    raise gen.Return(struct)

@gen.coroutine
def check_account_type(db, account, account_type):
    '''
        check account type
    '''
    try:
        check_type = yield db.accounts.find_one({'account': account,
                                                 'type':account_type},
                                                {'type':1, '_id':0})
    except Exception, e:
        logging.exception(e)
        raise e

        return

    raise gen.Return(check_type)

@gen.coroutine
def check_account_authorization(db, account, password):
    '''
        Check account authorization
    '''
    try:
        message = yield db.accounts.find_one({'account': account,
                                              'password': password})

    except Exception, e:
        logging.exception(e)
        raise e

        return

    raise gen.Return(message)

@gen.coroutine
def check_aggregation_pipeline(struct):
    '''
        Check aggregation pipeline

        Return mongodb aggregation report
    '''
    try:
        aggregation = reports.Aggregate(**struct).validate()
    except Exception, e:
        logging.exception(e)
        raise e

        return

    message = aggregation

    # TODO: test this in action
    
    raise gen.Return(message)
    
@gen.coroutine
def check_times(start, end):
    '''
        Check times
    '''
    try:
        start = (arrow.get(start) if start else arrow.get(arrow.utcnow().date()))
        end = (arrow.get(end) if end else start.replace(days=+1))

        start = start.timestamp
        end = end.timestamp

    except Exception, e:
        logging.exception(e)
        raise e

        return

    message = {'start':start, 'end':end}
    
    raise gen.Return(message)

@gen.coroutine
def check_times_get_timestamp(start, end):
    '''
        Check times
    '''
    try:
        start = (arrow.get(start) if start else arrow.get(arrow.utcnow().date()))
        end = (arrow.get(end) if end else start.replace(days=+1))
    except Exception, e:
        logging.exception(e)
        raise e

        return

    message = {'start':start.timestamp, 'end':end.timestamp}
    
    raise gen.Return(message)

@gen.coroutine
def check_times_get_datetime(start, end):
    '''
        Check times
    '''
    try:
        start = (arrow.get(start) if start else arrow.get(arrow.utcnow().date()))
        end = (arrow.get(end) if end else start.replace(days=+1))
    except Exception, e:
        logging.exception(e)
        raise e

        return

    message = {'start':start.naive, 'end':end.naive}
    
    raise gen.Return(message)

@gen.coroutine
def new_resource(db, struct, collection=None, scheme=None):
    '''
        New resource function
    '''
    import uuid as _uuid
    from schematics import models as _models
    from schematics import types as _types

    class StarfruitResource(_models.Model):
        '''
            Starfruit resource
        '''
        uuid = _types.UUIDType(default=_uuid.uuid4)
        account = _types.StringType(required=False)
        resource  = _types.StringType(required=True)


    # Calling getattr(x, "foo") is just another way to write x.foo
    collection = getattr(db, collection)  

    try:
        message = StarfruitResource(struct)
        message.validate()
        message = message.to_primitive()
    except Exception, e:
        logging.exception(e)
        raise e
        return

    resource = 'resources.{0}'.format(message.get('resource'))

    try:
        message = yield collection.update(
            {
                #'uuid': message.get(scheme),           # tha fucks ?
                'account': message.get('account')
            },
            {
                '$addToSet': {
                    '{0}.contains'.format(resource): message.get('uuid')
                },
                    
                '$inc': {
                    'resources.total': 1,
                    '{0}.total'.format(resource): 1
                }
            }
        )
    except Exception, e:
        logging.exception(e)
        raise e
        return

    raise gen.Return(message)

def clean_message(struct):
    '''
        clean message structure
    '''
    struct = struct.to_native()

    struct = {
        key: struct[key] 
            for key in struct
                if struct[key] is not None
    }

    return struct

def clean_structure(struct):
    '''
        clean structure
    '''
    struct = struct.to_primitive()

    struct = {
        key: struct[key] 
            for key in struct
                if struct[key] is not None
    }

    return struct

def clean_results(results):
    '''
        clean results
    '''
    results = results.to_primitive()
    results = results.get('results')

    results = [
        {
            key: dic[key]
                for key in dic
                    if dic[key] is not None 
        } for dic in results 
    ]

    return {'results': results}

def content_type_validation(handler_class):
    '''
        Content type validation
    
        @decorator
    '''

    def wrap_execute(handler_execute):
        '''
            Content-Type checker

            Wrapper execute function
        '''
        def ctype_checker(handler, kwargs):
            '''
                Content-Type checker implementation
            '''
            content_type = handler.request.headers.get("Content-Type", "")
            if content_type is None or not content_type.startswith('application/json'):
                handler.set_status(415)
                handler._transforms = []
                handler.finish({
                    'status': 415,
                    'reason': 'Unsupported Media Type',
                    'message': 'Must ACCEPT application/json: '\
                    '[\"%s\"]' % content_type 
                })
                return False
            return True

        def _execute(self, transforms, *args, **kwargs):
            '''
                Execute the wrapped function
            '''
            if not ctype_checker(self, kwargs):
                return False
            return handler_execute(self, transforms, *args, **kwargs)

        return _execute

    handler_class._execute = wrap_execute(handler_class._execute)
    return handler_class

def content_type_msgpack_validation(handler_class):
    '''
        Content-Type validation
        type: application/msgpack
        
        This function is a @decorator.
    '''

    def wrap_execute(handler_execute):
        '''
            Content-Type checker

            Wrapper execute function
        '''

        def content_type_checker(handler, kwargs):
            '''
                Content-Type checker implementation
            '''
            content_type = handler.request.headers.get('Content-Type', "")
            if content_type is None or not content_type.startswith('application/msgpack'):
                handler.set_status(415)
                handler._transforms = []
                handler.finish({
                    'status': 415,
                    'reason': 'Unsupported Media Type',
                    'message': 'Must ACCEPT application/msgpack: '\
                               '[\"%s\"]' % content_type
                })
                return False
            return True

        def _execute(self, transforms, *args, **kwargs):
            '''
                Execute the wrapped function
            '''
            if not content_type_checker(self, kwargs):
                return False
            return handler_execute(self, transforms, *args, **kwargs)

        return _execute

    handler_class._execute = wrap_execute(handler_class._execute)
    return handler_class


def zmq_external_logger(host='localhost', port='8899'):
    '''
        This publish logging messages over a zmq.PUB socket
    '''
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect('tcp://{0}:{1}'.format(host, port))
    handler = PUBHandler(socket)
    logger = logging.getLogger()
    logger.addHandler(handler)
    handler.root_topic = 'logging'
    return logger

def create_parser(description):
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-H', '--host', default='localhost',
                        help='Asterisk Manager hostname')
    parser.add_argument('-p', '--port', type=int, default=5038,
                        help='Asterisk Manager port number')
    parser.add_argument('-u', '--user', default="xivouser",
                        help='authentication username')
    parser.add_argument('-s', '--secret', default="xivouser",
                        help='authentication secret')

    parser.add_argument('-q', '--quiet', action='store_true',
                        help='hide information messages')
    parser.add_argument('--debug', action='store_true',
                        help='show debug messages')

    return parser


def parse_args(parser):
    args = parser.parse_args()
    options = CLIOptions()
    options.host, options.port = args.host, args.port
    options.username, options.secret = args.user, args.secret

    if args.quiet:
        level = logging.WARNING
    elif args.debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(stream=sys.stderr, level=level)

    return options, args


@gen.coroutine
def resource_exists(db, struct):
    '''
        resource_exists

        exist, exists, existed
    '''

@gen.coroutine
def last_modified(db, struct):
    '''
        last_modified

        exist, exists, existed
    '''

@gen.coroutine
def moved_permanently(db, struct):
    '''
        moved_permanently

        exist, exists, existed
    '''

@gen.coroutine
def moved_temporarily(db, struct):
    '''
        moved_temporarily

        exist, exists, existed
    '''

@gen.coroutine
def previously_existed(db, struct):
    '''
        previosly_existed

        exist, exists, existed
    '''

@gen.coroutine
def resource_exists(db, struct):
    '''
        resource_exists

        exist, exists, existed
    '''

@gen.coroutine
def forbidden_resource(db, struct):
    '''
        forbidden_resource

        exist, exists, existed
    '''

@gen.coroutine
def delete_resource(db, struct):
    '''
        delete_resource

        exist, exists, existed
    '''

@gen.coroutine
def delete_completed(db, struct):
    '''
        delete_resource
    '''