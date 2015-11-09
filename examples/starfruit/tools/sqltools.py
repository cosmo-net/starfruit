#!/usr/bin/env python
#

import MySQLdb

class MyDbStuff(object):

    def __init__(self, host, user, passwd, db):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db

        #DB Connection
        self.con = None

    def initialize(self):
        self.con = MySQLdb.connect(
            self.host,
            self.user,
            self.passwd,
            self.db
        )

    def disconnect(self):
        self.con.close()

    def sp_insert_stuff(self, sp, sp_value):
        self.initialize()
        cursor = self.con.cursor()
        cursor.callproc(sp, sp_value)
        cursor.close()

        self.con.commit()
        self.disconnect()

    def sp_return_stuff(self, sp, sp_value):
        self.initialize()
        cursor = self.con.cursor()
        cursor.callproc(sp, sp_value)
        result = cursor.fetchone()

        cursor.close()
        self.disconnect()

        return result
