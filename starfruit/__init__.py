"""
AMI adapter for the Tornado network programming framework.
"""

import tornado
import logging
import socket

from tornado.ioloop import IOLoop
from tornado.iostream import IOStream

import argparse
import sys

from starfruit.system.protocol import AMIProtocol

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


class StarfruitProtocol(AMIProtocol):

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

