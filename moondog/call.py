'''
    Asterisk Call File Generator.
'''

import os
import re
import tempfile
import logging


class CallException(Exception):
    pass

class CallError(CallException):
    pass

class CallFile(object):
    '''
        Asterisk Call File Generator.
    '''

    def __init__(self):
        self.params = {}
        self._file_options()

    def _file_options(self):
        fileargs = ('Channel', 'Callerid', 'MaxRetries', 'RetryTime',
                    'WaitTime', 'Context', 'Extension', 'Priority')

        for i in range(0, len(fileargs)):
            self.params[i] = fileargs[i]

    def input_args(self, path, args):
        if not re.search(r'^/(\w+\W?\w+)+/$', path):
            raise CallError('Invalid path: %s' % path)

        if len(args) != len(self.params):
            raise CallError('INPUT args %s NOT EQUAL file_options %s' % (len(args), len(self.params)))

    def generate_call(self, path, *args):
        self.input_args(path, args)

        (fd, path) = tempfile.mkstemp(suffix = '.call', dir = path)

        file = os.fdopen(fd, 'w')
        for i in range(0, len(args)):
            if i == 0:
                file.write(''.join((self.params[i], ': ', args[i])))
            else:
                file.write(''.join(('\n', self.params[i], ': ', args[i])))
        file.close()
        
        return path

if __name__=='__main__':
    testing = CallFile()
    x = testing.generate_call('/home/ooo/',
        'SIP/gocella_18777786075/18883829578',
        '18777786075',
        '5',
        '300',
        '45',
        'DID_18777786075',
        '18777786075',
        '1'
    )
    
    print x, 'sd the wishing well'
