#!/usr/bin/env python
# OMFG 1.0

from sqltools import MyDbStuff as _sql

con = _sql('192.168.1.29', 'root', 'S13r22eqwsql', 'asterisk')
con.initialize()

cursor = con.con.cursor()

exten = '8800'
date = '2010-07-27'
agent = 'jsibaja'
queue = 'out_lafise'
status = 'PEBKAC'

#SELECT * FROM asterisk.cdr where channel like 'SIP/8800%' and date(calldate) = '2010-07-26'
cursor.execute(''.join(('SELECT uniqueid FROM cdr WHERE channel like "SIP/', 
                         exten, '%" and date(calldate) = "', date, '"')))


data = cursor.fetchall()

print data

for x in data:
    #print ''.join(('INSERT INTO queues_outboundlog (uniqueid, queue_name, agent, status, notes) VALUES ("', x[0], '","', queue, '","', agent, '","', status, '","', status, '")'))
    cursor.execute(''.join(('INSERT INTO queues_outboundlog (uniqueid, queue_name, agent, status, notes) VALUES ("', x[0], '","', queue, '","', agent, '","', status, '","', status, '")')))
    #INSERT INTO queues_outboundlog (uniqueid, queue_name, agent, status, notes) VALUES ('111111111.1111', 'out_lafise', 'alpha', 'PEBKAC', 'PEBKAC');






