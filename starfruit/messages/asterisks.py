# -*- coding: utf-8 -*-
'''
    Starfruit asterisks models and messages.
'''

# This file is part of starfruit.

# Distributed under the terms of the last AGPL License.
# The full license is in the file LICENCE, distributed as part of this software.

__author__ = 'Jean Chassoul'


import arrow
import uuid

from schematics import models
from schematics import types


class Asterisk(models.Model):
    '''
        Asterisk Object Data Structure
    '''
    uuid = types.UUIDType(default=uuid.uuid4)
    account = types.StringType()
    user = types.StringType()
    secret = types.StringType()
    host = types.StringType()
    port = types.IntType(default=7542)
    primary = types.BooleanType(default=False)
    status = types.StringType(choices=['disable',
                                       'active',
                                       'suspended'],
                              default='disable',
                              required=True)
    checked = types.BooleanType(default=False)
    checked_by = types.StringType()
    created = types.DateTimeType(default=arrow.utcnow().naive)
    created_at = types.DateTimeType(default=arrow.utcnow().naive)
    last_modified = types.DateTimeType()
    updated_by = types.StringType()
    updated_at = types.DateTimeType()
    url = types.StringType()


class ModifyAsterisk(models.Model):
    '''
        Modify Asterisk

        This model is similar to Asterisk.

        It lacks of require and default values on it's fields.

        The reason of it existence is that we need to validate
        every input data that came from outside the system, with 
        this we prevent users from using PATCH to create fields 
        outside the scope of the resource.
    '''
    uuid = types.UUIDType()
    account = types.StringType()
    user = types.StringType()
    secret = types.StringType()
    host = types.StringType()
    port = types.IntType()
    primary = types.BooleanType()
    status = types.StringType()
    checked = types.BooleanType()
    checked_by = types.StringType()
    created = types.DateTimeType()
    created_at = types.DateTimeType()
    last_modified = types.DateTimeType()
    updated_by = types.StringType()
    updated_at = types.DateTimeType()
    url = types.StringType()