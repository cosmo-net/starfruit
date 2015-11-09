"""
AMI adapter for the Tornado network programming framework.
"""
import logging

from starfruit.system.protocol.ami import AMIProtocol

log = logging.getLogger(__name__)


class TornadoAdapter(object):
    """
    Tornado adapter for Obelus protocols (e.g. AMIProtocol, AGIProtocol).

    Pass a *protocol* instance to create the adapter, then call
    :meth:`bind_stream` when you need to wire the protocol to a Tornado
    :class:`~tornado.iostream.IOStream` instance.
    """

    stream = None

    def __init__(self, protocol):
        self.protocol = protocol

    def bind_stream(self, stream):
        """
        Bind the protocol to the given IOStream.  The stream should
        be already connected, as the protocol's connection_made() will
        be called immediately.
        """
        self.stream = stream
        self.stream.read_until_close(self._final_cb, self._streaming_cb)
        self.stream.set_close_callback(self._close_cb)
        self.protocol.connection_made(self)

    def _streaming_cb(self, data):
        if data:
            self.protocol.data_received(data)

    def _final_cb(self, data):
        # This is called when reading is finished, either because
        # of a regular EOF or because of an error.
        self._streaming_cb(data)
        self._close_cb()

    def _close_cb(self, *args):
        if self.stream is not None:
            stream = self.stream
            self.stream = None
            self.protocol.connection_lost(stream.error)

    def write(self, data):
        if self.stream is None:
            raise ValueError("write() on a non-connected protocol")
        self.stream.write(data)

    def close(self):
        if self.stream is not None:
            self.stream.close()


class CLIOptions(object):
    pass


class StarFruitProtocol(AMIProtocol):

    def __init__(self, loop, options):
        AMIProtocol.__init__(self)
        self.loop = loop
        self.options = options

        self.setup_event_handlers()

    def setup_event_handlers(self):
        """
        Setup the AMI event handlers required for call tracking.
        This is implicitly called on __init__().
        
        self.ami.register_event_handler('VarSet', self.on_var_set)
        self.ami.register_event_handler('LocalBridge', self.on_local_bridge)
        self.ami.register_event_handler('Dial', self.on_dial)
        self.ami.register_event_handler('Newstate', self.on_new_state)
        self.ami.register_event_handler('Hangup', self.on_hangup)
        # Yes, there's an event called "OriginateResponse"
        self.ami.register_event_handler('OriginateResponse', self.on_originate_response)
        """
        self.register_event_handler('Ping', self.do_on_ping)
        
    def connection_made(self, transport):
        log.info("Connection made")
        super(StarFruitProtocol, self).connection_made(transport)

    def connection_lost(self, exc):
        log.info("Connection lost")
        super(StarFruitProtocol, self).connection_lost(exc)
        self.loop.stop()

    def greeting_received(self, api_name, api_version):
        log.info("Asterisk greeting: %r, %r", api_name, api_version)

        a = self.send_action('Login', {'username': self.options.get('username'),
                                       'secret': self.options.get('secret')})
        a.on_result = self.login_successful
        a.on_exception = self.login_failed

    def login_successful(self, resp):
        log.info("Successfully logged in")
        a = self.send_action('Ping', {})
        a.on_result = self.pong
        a.on_exception = self.ping_failed

    def login_failed(self, exc):
        log.error("Failed logging in: %s", exc)
        self.transport.close()

    def do_on_ping(self, event):
        h = event.headers
        log.info(h)

    def pong(self, resp):
        log.info("Pong")

        b = self.send_action('QueueSummary', {})
        b.on_result = self.pongo
        b.on_exception = self.pingo_failed

    def ping_failed(self, exc):
        log.error("Failed ping in: %s", exc)

    def pingo_failed(self, exc):
        log.error("Failed ping in: %s", exc)

    def pongo(self, resp):
        log.info('b response ListCommands')
        log.info(resp)

