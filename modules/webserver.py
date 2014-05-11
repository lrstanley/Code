from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
import threading
import thread
import time
from random import randint as gen
from util import output

# Example command...
#  - http://your-host.net:8888/?pass=herpderptrains&args=PRIVMSG+%23L&data=Testing+123
host = '0.0.0.0'

# Not important
data, password = [], None


class WebServer(BaseHTTPRequestHandler):
    """The actual webserver that responds to things that received via GET queries."""
    def do_GET(self):
        args = {}
        path = self.path
        global data
        if '?' in path:
            tmp = path.split('?', 1)[1]
            args = urlparse.parse_qs(tmp)
            data.append(args)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()


class CollectData(threading.Thread):
    def __init__(self, code, input, id):
        super(CollectData, self).__init__()
        self.daemon = True
        self.code = code
        self.input = input
        self.id = id
        self.password = self.code.config.webserver_pass

    def run(self):
        global data
        while True:
            if self.code.get('webserver.object') != self.id:
                return False
            time.sleep(1)
            if len(data) < 1:
                continue
            # Parse data before we do anything with it
            try:
                event = data[0]
                del data[0]

                if 'pass' not in event:
                    continue
                if event['pass'][0] != self.password:
                    continue

                # Authenticated.. Now we need to find some variables in the event
                # 1. args (used for IRC commands)
                # 2. data (The argument for the IRC command (the arguments argument!))
                if 'args' not in event or 'data' not in event:
                    continue
                self.code.write(event['args'][0].split(), self.code.format(event['data'][0]))
            except:
                continue


def init(host, port):
    """Tries to start the webserver. Fails if someone initiates a reload, or port is already in use."""
    try:
        time.sleep(5)
        server = HTTPServer(('0.0.0.0', port), WebServer)
        output.success('Starting HTTP server on %s:%s' % (host, port), 'WEBSERVER')
    except:
        return
    server.serve_forever()


def setup(code):
    id = str(gen(0, 10000000))
    code.set('webserver.object', id)

    # Nasty area, we check for configuration options, some are required and some arent
    if not hasattr(code.config, 'run_webserver') or not hasattr(code.config, 'webserver_pass'):
        return
    if not code.config.run_webserver:
        return
    if not code.config.webserver_pass:
        output.error('To use webserver.py you must have a password setup in default.py!')
        return
    if not hasattr(code.config, 'webserver_port'):
        port = 8888
    else:
        port = code.config.webserver_port
    Sender = CollectData(code, input, id)
    Sender.start()  # Initiate the thread.
    thread.start_new_thread(init, (str(host), int(port),))
