"""
AMI adapter for the Tornado network programming framework.
"""

import tornado
import logging
import socket

from tornado.ioloop import IOLoop
from tornado.iostream import IOStream
from starfruit import TornadoAdapter




if __name__ == "__main__":
    

    from . import examplecli

    parser = examplecli.create_parser(
        description="Tornado-based AMI client example")

    options, args = examplecli.parse_args(parser)

    log = logging.getLogger(__name__)

    loop = IOLoop.instance()
    proto = examplecli.CLIProtocol(loop, options)
    adapter = TornadoAdapter(proto)

    stream = IOStream(socket.socket(), loop)
    stream.connect((options.host, options.port),
                   lambda: adapter.bind_stream(stream))

    try:
        loop.start()
    except KeyboardInterrupt:
        pass
