# -*- coding: utf-8 -*-
'''
    Starfruit tools system periodic functions.
'''

# This file is part of starfruit.

# Distributed under the terms of the last AGPL License. 
# The full license is in the file LICENCE, distributed as part of this software.

__author__ = 'Jean Chassoul'

import logging
from tornado import httpclient
import ujson as json
import uuid
import urllib
import motor
import queries

#import address

from contextlib import contextmanager
from tornado import gen

# from starfruit.messages import accounts

#from starfruit.system import records


from bson import objectid


httpclient.AsyncHTTPClient.configure('tornado.curl_httpclient.CurlAsyncHTTPClient')


@gen.coroutine
def get_coturn_tasks(db):
    '''
        Get coturn label tasks
    '''
    tasks_list = []
    try:
        query = db.tasks.find(
            {'label':'coturn',
             'assigned': False}, 
            {'_id':0} # 'account':1, 'uuid':1,
        )
        while (yield query.fetch_next):
            task = query.next_object()
            tasks_list.append(task)
    except Exception, e:
        logging.exception(e)
        raise gen.Return(e)

    raise gen.Return(tasks_list)

@gen.coroutine
def get_raw_records(sql, query_limit):
    '''
        Get RAW records
    '''
    http_client = httpclient.AsyncHTTPClient()

    def handle_restuff(response):
        '''
            Request Handler Restuff
        '''
        if response.error:
            logging.error(response.error)
        else:
            logging.info(response.body)

    def handle_request(response):
        '''
            Request Handler
        '''
        if response.error:
            logging.error(response.error)
        else:

            logging.info(response.body)

            res = json.loads(response.body)

            request_id = res.get('uuid', None)
            if request_id:
                request_id = request_id.get('uuid')

            http_client.fetch(
                'http://iofun.io/records/{0}'.format(request_id), 
                headers={"Content-Type": "application/json"},
                method='GET',

                #body=json.dumps(record),

                callback=handle_restuff
            )


            # if successful response we need to send ack now to sql
            # and mack the flag of that call as checked, otherwise
            # we need some other type of validation.


    try:
        # Get SQL database from starfruit settings
        query = '''
            SELECT
                DISTINCT ON (uniqueid) uniqueid,
                src as source,
                dst as destination,
                dcontext,
                channel,
                dstchannel,
                lastapp,
                lastdata,
                duration,
                billsec,
                disposition,
                checked

            FROM cdr

            WHERE checked = false

            ORDER BY uniqueid DESC

            LIMIT {0};
        '''.format(
            query_limit
        )
        result = yield sql.query(query)

        if result:

            logging.info(len(result)) 

            for row in result:

                record = dict(row.items())

                http_client.fetch(
                    'http://iofun.io/records/', 
                    headers={"Content-Type": "application/json"},
                    method='POST',
                    body=json.dumps(record),
                    callback=handle_request
                )

            message = {'ack': True}
        else:
            message = {'ack': False}

        result.free()

        logging.warning('get raw records spawned on PostgreSQL {0}'.format(message))
        
    except Exception, e:
        logging.exception(e)
        raise e

    raise gen.Return(message)

@gen.coroutine
def get_usernames(db):
    '''
        Get all the username accounts
    '''
    usernames = []
    try:
        query = db.accounts.find(
            {}, 
            {'account':1, 'uuid':1, '_id':0}
        )
        while (yield query.fetch_next):
            account = query.next_object()
            usernames.append(account)
    except Exception, e:
        logging.exception(e)
        raise gen.Return(e)

    raise gen.Return(usernames)

@gen.coroutine
def get_unassigned_call(db):
    '''
        Get 'one thousand' unassigned calls.
    '''
    try:
        result = []

        query = db.calls.find({
            'assigned': {
                '$exists': False
            }
        }).limit(800)
        
        for call in (yield query.to_list()):
            result.append(call)
            
    except Exception, e:
        logging.exception(e)
        raise gen.Return(e)
    
    raise ren.Return(result)

@gen.coroutine
def process_assigned_false(db):
    '''
        Periodic task that process 'one thousand' 
        assigned False flag on calls resource.
    '''

    message = []

    def got_record(record, error):
        '''
            got record
        '''
        if record:
            channel = (record['channel'] if 'channel' in record else False)

            if channel:
                account = [a for a in account_list 
                           if ''.join(('/', a['account'], '-')) in channel]

                account = (account[0] if account else False)

                if account:
                    struct = {
                        'account':account['account'],
                        'resource':'records',
                        'id':record['_id']
                    }
                    message.append(struct)
        elif error:
            logging.error(error)
            return error
        else:
            logging.info('got record function result: {0}'.format(message))
            return message
    try:

        account_list = yield get_usernames(db)

        db.records.find({
            'assigned':False
        }).limit(1000).each(got_record)
    except Exception, e:
        logging.exception(e)
        raise gen.Return(e)

@gen.coroutine
def process_assigned_records(db):
    '''
        Periodic task that process 'one thousand' 
        unassigned calls resource.
    '''
    result = []

    def _got_record(message, error):
        '''
            got record
        '''
        if error:
            logging.error(error)
            return error

        elif message:
            channel = (True if 'channel' in message else False)
            # get channel the value
            channel = (message['channel'] if channel else channel)

            if channel:
                account = [a for a in _account_list
                           if ''.join(('/', a['account'], '-')) in channel]
                account = (account[0] if account else False)

                if account:
                    struct = {
                        'account':account['account'],
                        'resource':'calls',
                        'id':message['_id']
                    }
                    result.append(struct)    
        else:
            #logging.info('got record result: %s', result)
            return result

    try:
        _account_list = yield get_usernames(db)

        db.calls.find({
            'assigned':{'$exists':False}
        }).limit(800).each(_got_record)
    except Exception, e:
        logging.exception(e)
        raise gen.Return(e)

@gen.coroutine
def assign_record(db, account, callid): # , struct
    '''
        Update record assigned flag
    '''
    #recs = records.Records()
    try:
        result = yield db.calls.update(
            {'_id':objectid.ObjectId(callid)}, 
            {'$set': {'assigned': True,
                      'accountcode':account}}
        )
        #result = yield recs.new_detail_record(struct)

    except Exception, e:
        logging.exception(e)
        raise e

        return

    raise gen.Return(result)

@gen.coroutine
def checked_flag(sql, uniqueid):
    '''
        periodic checked flag
    '''
    message = False
    try:
        query = '''
            UPDATE cdr set checked = true where uniqueid = '{0}'
        '''.format(uniqueid)
        result = yield sql.query(query)
        if len(result) > 0:
            message = True
        result.free()
    except Exception, e:
        logging.exception(e)
        raise e

    raise gen.Return(message)

@gen.coroutine
def get_query_records(sql, query_limit):
    '''
        periodic query records function
    '''
    logging.info('a little brain dead recolection of records')
    record_list = []

    http_client = httpclient.AsyncHTTPClient()

    def handle_record_uuid(response):
        '''
            Request Handler Record UUID
        '''
        if response.error:
            logging.error(response.error)
        else:
            logging.info(response.body)

    def handle_request(response):
        '''
            Request Handler
        '''
        if response.error:
            logging.error(response.error)
        else:
            logging.info(response.body)

            result = json.loads(response.body)

            request_id = result.get('uuid', None)
            if request_id:
                request_id = request_id.get('uuid')

            http_client.fetch(
                'http://iofun.io/records/{0}'.format(request_id), 
                headers={"Content-Type": "application/json"},
                method='GET',
                callback=handle_record_uuid
            )

    try:
        # Get SQL database from system settings
        # PostgreSQL insert new sip account query
        query = '''
            SELECT
                DISTINCT ON (uniqueid) uniqueid,
                calldate as start,
                date(calldate) as strdate,
                clid as callerid,
                src as source,
                dst as destination,
                dcontext as destination_context,
                channel,
                dstchannel as destination_channel,
                duration,
                billsec,
                billsec as seconds,
                disposition,
                checked 
            FROM cdr 
            WHERE checked = false
            ORDER BY uniqueid DESC
            LIMIT {0};
        '''.format(
            query_limit
        )
        result = yield sql.query(query)

        logging.warning('Getting {0} rows from PostgreSQL'.format(len(result)))

        for x in result:
            record_list.append(x)

        result.free()

        # TODO: Still need to check the follings exceptions with the new queries module.
        #except (psycopg2.Warning, psycopg2.Error) as e:
        #    logging.exception(e)
        #    raise e
        
    except Exception, e:
        logging.exception(e)
        raise e

    raise gen.Return(record_list)