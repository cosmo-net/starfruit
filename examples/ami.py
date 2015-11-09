'''
This module provides a Python API for interfacing with the asterisk manager.
'''

import starfruit.ami
import sys

def handle_shutdown(event, manager):
    print "Recieved shutdown event"
    manager.close()
    # we could analize the event and reconnect here
    
def handle_event(event, manager):
    print "Recieved event: %s" % event.name

manager = starfruit.ami.Manager()
try:
    # connect to the manager
    try:
       manager.connect('host') 
       manager.login('user', 'secret')

          # register some callbacks
           manager.register_event('Shutdown', handle_shutdown) # shutdown
           manager.register_event('*', handle_event)           # catch all
           
           # get a status report
           response = manager.status()

           manager.logoff()
       except starfruit.ami.ManagerSocketException, (errno, reason):
          print "Error connecting to the manager: %s" % reason
          sys.exit(1)
       except starfruit.ami.ManagerAuthException, reason:
          print "Error logging in to the manager: %s" % reason
          sys.exit(1)
       except starfruit.ami.ManagerException, reason:
          print "Error: %s" % reason
          sys.exit(1)
          
   finally:
      # remember to clean up
      manager.close()

# Remember all header, response, and event names are case sensitive.
#
# Not all manager actions are implmented as of yet, feel free to add them
# and submit patches.