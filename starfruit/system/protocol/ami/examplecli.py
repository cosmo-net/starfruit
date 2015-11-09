import argparse
import logging
import sys

from starfruit.system.protocol.ami import AMIProtocol

log = logging.getLogger(__name__)


class CLIOptions(object):
    pass


class CodeMachineProtocol(AMIProtocol):

    def __init__(self, loop, options):
        AMIProtocol.__init__(self)
        self.loop = loop
        self.options = options

    def connection_made(self, transport):
        log.info("Connection made")
        super(CodeMachineProtocol, self).connection_made(transport)

    def connection_lost(self, exc):
        log.info("Connection lost")
        super(CodeMachineProtocol, self).connection_lost(exc)
        self.loop.stop()

    def greeting_received(self, api_name, api_version):
        log.info("Asterisk greeting: %r, %r", api_name, api_version)

        a = self.send_action('Login', {'username': self.options.username,
                                       'secret': self.options.secret})
        a.on_result = self.login_successful
        a.on_exception = self.login_failed

    def login_successful(self, resp):
        log.info("Successfully logged in")

        context = 'fun-raymond'
        priority = '1'
        timeout = '45'
        caller_id = '17028293110'
        account = '3090'
        headers = {
            'Channel': 'SIP/3091',
            'Exten': '3091',
            'context': context,
            'priority': priority,
            'timeout': timeout,
            'caller_id': caller_id,
            'account': account
        }

       
        a = self.send_action('Ping', {})
        a.on_result = self.pong
        a.on_exception = self.ping_failed

    def login_failed(self, exc):
        log.error("Failed logging in: %s", exc)
        self.transport.close()

    def pong(self, resp):
        log.info("Pong")

    def ping_failed(self, exc):
        log.error("Failed ping in: %s", exc)
        


class CLIProtocol(AMIProtocol):

    def __init__(self, loop, options):
        AMIProtocol.__init__(self)
        self.loop = loop
        self.options = options

    def connection_made(self, transport):
        log.info("Connection made")
        super(CLIProtocol, self).connection_made(transport)

    def connection_lost(self, exc):
        log.info("Connection lost")
        super(CLIProtocol, self).connection_lost(exc)
        self.loop.stop()

    def greeting_received(self, api_name, api_version):
        log.info("Asterisk greeting: %r, %r", api_name, api_version)

        a = self.send_action('Login', {'username': self.options.username,
                                       'secret': self.options.secret})
        a.on_result = self.login_successful
        a.on_exception = self.login_failed

    def login_successful(self, resp):
        log.info("Successfully logged in")
        
        '''
        from obelus.ami import CallManager

        from obelus.ami import Call

        cm = CallManager(self)

        class TestCall(Call):

            def dialing_started(self):
                log.info('tomela')

        tc = TestCall()

        log.info('tons?')
        cm.originate(tc, {})
        '''

        log.warning("stufa")

    def login_failed(self, exc):
        log.error("Failed logging in: %s", exc)
        self.transport.close()


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
