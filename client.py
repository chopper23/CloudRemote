
"""
Simple Web socket client implementation using Tornado framework.
Adapted from:
    http://code.activestate.com/recipes/579076-simple-web-socket-client-\
    implementation-using-torn/
Usage Example:
    # stream messages to console
    python websocket_client.py -s 127.0.0.1:9090/websocket
    # stream messages to log
    python websocket_client.py -s 127.0.0.1:9090/websocket > socket.log
"""
from __future__ import print_function
# lib
import argparse
import functools
import json
import time
# third party
from tornado import escape
from tornado import gen
from tornado import httpclient
from tornado import httputil
from tornado import ioloop
from tornado import websocket
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

channel = 16

GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def my_callback(channel):
    #server = "ws://%s" % (args.socket or '192.168.1.239/socket/')
    server = "ws://192.168.1.239/socket/"
    client = TestWebSocketClient()
    client.connect(server)

GPIO.add_event_detect(channel, GPIO.RISING, callback=my_callback, bouncetime=500) 



APPLICATION_JSON = 'application/json'

DEFAULT_CONNECT_TIMEOUT = 60
DEFAULT_REQUEST_TIMEOUT = 60
toggle = 'lightoff'

class WebSocketClient(object):
    """Base for web socket clients.
    """

    def __init__(self, connect_timeout=DEFAULT_CONNECT_TIMEOUT,
                 request_timeout=DEFAULT_REQUEST_TIMEOUT):
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self._ws_connection = None

    def connect(self, url):
        """Connect to the server.
        :param str url: server URL.
        """
        headers = httputil.HTTPHeaders({'Content-Type': APPLICATION_JSON})
        request = httpclient.HTTPRequest(url=url,
                                         connect_timeout=self.connect_timeout,
                                         request_timeout=self.request_timeout,
                                         headers=headers)
        ws_conn = websocket.WebSocketClientConnection(ioloop.IOLoop.current(),
                                                      request)
        ws_conn.connect_future.add_done_callback(self._connect_callback)

    def send(self, data):
        """Send message to the server
        :param str data: message.
        """
        if not self._ws_connection:
            raise RuntimeError('Web socket connection is closed.')
        self._ws_connection.write_message(escape.utf8(json.dumps(data)))

    def close(self):
        """Close connection.
        """
        if not self._ws_connection:
            raise RuntimeError('Web socket connection is already closed.')
        self._ws_connection.close()

    def _connect_callback(self, future):
        """Callback
        """
        if future.exception() is None:
            self._ws_connection = future.result()
            self._on_connection_success()
            self._read_messages()
        else:
            self._on_connection_error(future.exception())

    @gen.coroutine
    def _read_messages(self):
        """Access messages
        """
        while True:
            msg = yield self._ws_connection.read_message()
            if msg is None:
                self._on_connection_close()
                break
            self._on_message(msg)

    def _on_message(self, msg):
        """This is called when new message is available from the server.
        :param str msg: server message.
        """
        pass

    def _on_connection_success(self):
        """This is called on successful connection ot the server.
        """
        pass

    def _on_connection_close(self):
        """This is called when server closed the connection.
        """
        pass

    def _on_connection_error(self, exception):
        """This is called in case if connection to the server could
        not established.
        """
        pass


class TestWebSocketClient(WebSocketClient):
    """Implementation of a web socket client.
    """

    def _on_message(self, msg):
        print(msg)
        #deadline = time.time() + 1
        #ioloop.IOLoop().instance().add_timeout(
        #    deadline, functools.partial(self.send, str(int(time.time()))))

    def _on_connection_success(self):
        print('Connected!')
        #return WebSocketClient.send(self, {'cmd':'scene','val':'storm'})
        global toggle
        if (toggle == 'lamp'):
            toggle = 'lightoff'
        else:
            toggle = 'lamp'
        return WebSocketClient.send(self, {'cmd':'light','val':toggle})
            

    def _on_connection_close(self):
        print('Connection closed!')

    def _on_connection_error(self, exception):
        print('Connection error: %s', exception)
        
    

def main(args):
    """Process args and setup streams."""
    #testing = args.test or False

    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        client.close()


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument(
        '-s', '--socket',
        help="Server name, with port, for the WebSocket Server")
    PARSER.add_argument(
        '-e', '--test',
        default=False,
        action='store_true',
        help="Whether to run system in TEST mode")
    ARGS = PARSER.parse_args()
    main(ARGS)