# -*- coding: utf-8 -*-
'''
    Starfruit HTTP base handlers.
'''

# This file is part of starfruit.

# Distributed under the terms of the last AGPL License.
# The full license is in the file LICENCE, distributed as part of this software.

__author__ = 'Jean Chassoul'


import time
import motor
import queries

from tornado import gen
from tornado import web

from zmq.eventloop import ioloop


from starfruit.messages import asterisks as _asterisks

from starfruit.tools import clean_structure
from starfruit.tools import check_account_authorization

from starfruit import errors

from starfruit.tools.quotes import PeopleQuotes

import logging


# msg means message

# dht means distributed hash table

# share hash table missing. cebus integration? 

# cebus missing completetly.

# but on the other hand overlords start to make sense.


class BaseHandler(web.RequestHandler):
    '''
        System application request handler

        gente d'armi e ganti
    '''

#    @gen.coroutine
#    def prepare(self):
#        yield super().prepare() or gen.moment

    @property
    def sql(self):
        '''
            SQL database
        '''
        return self.settings['sql']

    @property
    def document(self):
        '''
            Document database
        '''
        return self.application.document

    @property
    def kvalue(self):
        '''
            Key-value database
        '''
        return self.application.kvalue

    @property
    def cache(self):
        '''
            Cache backend
        '''
        return self.settings['cache']

    def initialize(self, **kwargs):
        '''
            Initialize the Base Handler
        '''
        # Service Process Quality Management
        #===================================

        # The Senate and People of Mars
        # -----------------------------
        # SPQM communication messages.

        # 0MQ message streams
        # --------------------

        # CDR stream
        # self.cdr_stream = self.settings['cdr_stream'] || or just subscribe to the cdr topic on SUB.

        # CDR periodic channel, why channel? the world channel, etc.
        # self.cdr_periodic = self.settings['cdr_periodic']

        super(BaseHandler, self).initialize(**kwargs)

        self.etag = None

        # System database
        self.db = self.settings['db']

        # Page settings
        self.page_size = self.settings['page_size']

    def set_default_headers(self):
        '''
            Starfruit default headers
        '''
        # if debug set allow all if not set settings domain
        self.set_header("Access-Control-Allow-Origin", '*')
        # self.set_header("Access-Control-Allow-Origin", self.settings['domain'])

    def get_current_username(self):
        '''
            Return the username from a secure cookie
        '''
        return self.get_secure_cookie('username')

    def get_current_account(self):
        '''
            Return the account from a secure cookie
        '''
        return self.get_secure_cookie('account')

    @gen.coroutine
    def let_it_crash(self, struct, scheme, error, reason):
        '''
            Let it crash
        '''
        # missing zmq sub topic
        str_error = str(error)
        error_handler = errors.Error(error)
        messages = []

        if error and 'Model' in str_error:
            message = error_handler.model(scheme)
        elif error and 'duplicate' in str_error:
            for name, value in reason.get('duplicates'):
                if value in str_error:
                    message = error_handler.duplicate(
                        name.title(),
                        value,
                        struct.get(value)
                    )
                    messages.append(message)
            message = ({'messages':messages} if messages else False)
        elif error and 'value' in str_error:
            message = error_handler.value()
        elif error is not None:
            logging.warning(str_error)
            logging.error(struct, scheme, error, reason)
            message = {
                'error': u'nonsense',
                'message': u'there is no error'
            }
        else:
            quotes = PeopleQuotes()
            message = {
                'status': 200,
                'message': quotes.get()
            }
        raise gen.Return(message)

    @gen.coroutine
    def remove_sip_account(self, struct):
        '''
            Remove sip account
        '''
        try:
            # Get SQL database from system settings
            sql = self.settings.get('sql')
            # PostgreSQL remove delete sip account query
            query = '''
                delete 
            '''
            message = query
        except Exception, e:
            logging.exception(e)
            raise e

        raise gen.Return(message)

    @gen.coroutine
    def new_sip_account(self, struct):
        '''
            New sip account
        '''
        try:
            # Get SQL database from system settings
            sql = self.settings.get('sql')
            # PostgreSQL insert new sip account query
            query = '''
                insert into sip (
                    name,
                    defaultuser,
                    fromuser,
                    fromdomain,
                    host,
                    sippasswd,
                    allow,
                    context,
                    nat,
                    qualify,
                    avpf,
                    encryption
                ) values (
                    '{0}',
                    '{1}',
                    '{2}',
                    '{3}',
                    'dynamic',
                    '{4}',
                    'ulaw,alaw,g729,gsm',
                    'fun-accounts',
                    'force_rport,comedia',
                    'yes',
                    'no',
                    'no'
                );
            '''.format(
                struct.get('account'),
                struct.get('account'),
                struct.get('account'),
                struct.get('domain', self.settings.get('domain')),
                struct.get('password')
            )
            result = yield sql.query(query)
            if result:
                message = {'ack': True}
            else:
                message = {'ack': False}
            result.free()
            logging.warning('new sip account spawned on PostgreSQL {0}'.format(message))

        # TODO: Still need to check the follings exceptions with the new queries module.
        #except (psycopg2.Warning, psycopg2.Error) as e:
        #    logging.exception(e)
        #    raise e
        
        except Exception, e:
            logging.exception(e)
            raise e

        raise gen.Return(message)

    @gen.coroutine
    def new_coturn_account(self, struct):
        '''
            New coturn account task
        '''
        try:
            task = _tasks.Task(struct)
            task.validate()
        except Exception, e:
            logging.exception(e)
            raise e

        task = clean_structure(task)

        result = yield self.db.tasks.insert(task)

        raise gen.Return(task.get('uuid'))

    @gen.coroutine
    def new_address(self, struct):
        '''
            New address
        '''
        try:
            address = _addresses.Address(struct)
            address.validate()
        except Exception, e:
            logging.exception(e)
            raise e

        address = clean_structure(address)

        result = yield self.db.addresses.insert(address)

        raise gen.Return(address.get('uuid'))


class CarambolaHandler(BaseHandler):
    '''
        Carambola Handler Quote experiment
    '''

    @gen.coroutine
    def get(self):
        '''
            Get some quotes
        '''
        quotes = PeopleQuotes()
        self.finish(
            {'quote': quotes.get()}
        )
