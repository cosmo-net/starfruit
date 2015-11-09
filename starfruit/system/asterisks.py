# -*- coding: utf-8 -*-
'''
    Starfruit asterisks system logic functions.
'''

# This file is part of stafruit.

# Distributed under the terms of the last AGPL License.
# The full license is in the file LICENCE, distributed as part of this software.

__author__ = 'Jean Chassoul'


import logging

import arrow
import motor

import uuid

# import numpy as np
import pandas as pd

from tornado import gen

from stafruit.messages import asterisks
from stafruit.messages import reports # WTF?

from starfruit.tools import clean_structure
from starfruit.tools import clean_results
from starfruit.tools import check_times


class Asterisks(object):
    '''
        Asterisks resources
    '''

    @gen.coroutine
    def get_asterisk(self, account, asterisk_uuid):
        '''
            Get a detail asterisk
        '''
        if not account:
            asterisk = yield self.db.asterisks.find_one({'uuid':asterisk_uuid},{'_id':0})
        else:
            asterisk = yield self.db.asterisks.find_one({
                'uuid':asterisk_uuid,
                'account':account
            },{'_id':0})
        try:
            if asterisk:
                asterisk = asterisks.Asterisk(asterisk)
                asterisk.validate()
        except Exception, e:
            # catch some daemon here!
            # so we send the exception down the drain, down the the rat hole, the rabbit hole, etc
            # but, it does not disapeer, if everything is set, the monitor,supervisor,overlord will know.
            logging.exception(e) 
            raise e
        # we use this last finally to raise gen.Return only because of python version 2.7 stuff
        finally:
            raise gen.Return(asterisk)

    @gen.coroutine
    def get_asterisk_list(self, account, start, end, lapse, status, page_num):
        '''
            Get detail asterisks 
        '''
        page_num = int(page_num)
        page_size = self.settings['page_size']
        asterisk_list = []
        message = None
        query = {'public':False}

        if status != 'all':
            query['status'] = status
        
        if not account:
            query = self.db.asterisks.find(query,
                                       {'_id':0, 'comments':0})
        elif type(account) is list:
            # really?
            accounts = [{'accountcode':a, 'assigned': True} for a in account]
            query = self.db.asterisks.find({'$or':accounts},
                                       {'_id':0, 'comments':0})
        else:
            query = self.db.asterisks.find({'accountcode':account,
                                        'assigned':True},
                                       {'_id':0, 'comments':0})
        
        query = query.sort([('uuid', -1)]).skip(page_num * page_size).limit(page_size)
        
        try:
            
            while (yield query.fetch_next):
                result = query.next_object()
                asterisk_list.append(asterisks.Asterisk(result))

        except Exception, e:
            logging.exception(e)
            raise e

        try:
            struct = {'results': asterisk_list}

            # reports BaseGoal? da faq??
            
            message = reports.BaseGoal(struct)
            message.validate()
            message = clean_results(message)

        except Exception, e:
            logging.exception(e)
            raise e
        finally:
            raise gen.Return(message)
    
    @gen.coroutine
    def get_unassigned_asterisks(self, start, end, lapse, page_num):
        '''
            Get unassigned asterisks
        '''
        page_num = int(page_num)
        page_size = self.settings['page_size']
        result = []
        
        # or $exist = false ?

        query = self.db.asterisks.find({'assigned':False})
        query = query.sort([('uuid', -1)]).skip(page_num * page_size).limit(page_size)
        
        try:
            for asterisk in (yield query.to_list()):
                result.append(asterisks.Asterisk(asterisk))
            
            struct = {'results':result}

            results = reports.BaseResult(struct)
            results.validate()
        except Exception, e:
            logging.exception(e)
            raise e

        results = clean_results(results)        
        raise gen.Return(results)


    @gen.coroutine
    def new_asterisk(self, struct):
        '''
            Create a new asterisk entry
        '''
        try:
            asterisk = asterisks.Asterisk(struct)
            asterisk.validate()
        except Exception, e:
            logging.exception(e)
            raise e

        asterisk = clean_structure(asterisk)

        result = yield self.db.asterisks.insert(asterisk)

        raise gen.Return(asterisk.get('uuid'))

    @gen.coroutine
    def set_assigned_flag(self, account, asterisk_uuid):
        '''
            Set the asterisk assigned flag
        '''
        logging.info('set_assigned_flag account: %s, asterisk: %s' % (account, asterisk_uuid))

        result = yield self.db.asterisks.update(
                                {'uuid':asterisk_uuid, 
                                 'accountcode':account}, 
                                {'$set': {'assigned': True}})
        
        raise gen.Return(result)

    @gen.coroutine
    def remove_asterisk(self, asterisk_uuid):
        '''
            Remove a asterisk entry
        '''
        result = yield self.db.asterisks.remove({'uuid':asterisk_uuid})
        raise gen.Return(result)

    @gen.coroutine
    def modify_asterisk(self, account, asterisk_uuid, struct):
        '''
            Modify asterisk
        '''
        try:
            logging.info(struct)
            asterisk = asterisks.ModifyAsterisk(struct)
            asterisk.validate()
            asterisk = clean_structure(asterisk)
        except Exception, e:
            logging.error(e)
            raise e

        try:
            result = yield self.db.asterisks.update(
                {'account':account,
                 'uuid':asterisk_uuid},
                {'$set':asterisk}
            )
            logging.info(result)            
        except Exception, e:
            logging.error(e)
            message = str(e)

        raise gen.Return(bool(result.get('n')))

    @gen.coroutine
    def replace_asterisk(self, struct):
        '''
            Replace a existent asterisk entry
        '''
        # put implementation
        pass

    @gen.coroutine
    def resource_options(self):
        '''
            Return resource options
        '''
        # options implementation
        pass