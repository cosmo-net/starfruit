'''
    This Module contains all the tools you need to generate '.call' 
    files for Asterisk.

    Channel: DAHDI/g1/11235813
    Callerid: 1123
    MaxRetries: 5
    RetryTime: 300
    WaitTime: 45
    Context: numberplan-custom-1
    Extension: 5813
    Priority: 1

'''

#Example:

from starfruit.call import CallFile

testing = CallFile()
    
testing.generate_call(
    '/var/spool/asterisk/outgoing/',
    'DAHDI/g1/11235813',
    '1123',
    '5',
    '300',
    '45',
    'numberplan-custom-1',
    '5813',
    '1'
)

#Remember to add the complete path where you like to store the .call 
#file and pass all the file arguments to the generate_call() method.