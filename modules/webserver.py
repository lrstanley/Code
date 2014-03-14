#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
webserver.py - Code Webserver-API Module
http://code.liamstanley.io/
"""

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
import cgi
import threading, thread
import time
from random import randint as gen

# Example command...
#  - http://your-host.net:8888/?pass=yoloswag&args=PRIVMSG+%23L&data=Testing+123
host = '0.0.0.0'
port = 8888


class WebServer(BaseHTTPRequestHandler):
    """The actual webserver that responds to things that received via GET queries."""
    def do_GET(self):
        args = {}
        path = self.path
        global data
        if '?' in path:
            path, tmp = path.split('?', 1)
            args_tmp = urlparse.parse_qs(tmp)
            for name, data in args_tmp.iteritems():
                args[name] = data[0]
            data.append(args)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()


data = []
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
            time.sleep (2)
            if len(data) < 1:
                continue
            # Parse data before we do anything with it
            try:
                for query in data:
                    # Query is everything that's sent, as a dict()
                    if not 'pass' in query: continue
                    if query['pass'] != self.password: continue

                    # Authenticated.. Now we need to find some variables in the query
                    # 1. args (used for IRC commands)
                    # 2. data (The arguement for the IRC command (the arguements arguement!))
                    if not 'args' in query or not 'data' in query: continue
                    self.code.write(query['args'].split(), query['data'])
            except:
                print '[ERROR] Failed to parse data! (%s)' % data
                continue
            data = []


def init(host, port):
    """Tries to start the webserver. Fails if someone initiates a reload, or port is already in use."""
    try:
        server = HTTPServer(('0.0.0.0', 8888), WebServer)
        print('[WEBSERVER] Starting HTTP server on %s:%s' % (host, port))
    except:
        print '[ERROR] Webserver already started.'
        return
    server.serve_forever()


started, password = False, None
def initFromIRC(code, input):
    global started
    if started == True:
        return

    started = True
    id = str(gen(0,10000000))
    code.set('webserver.object', id)

    # Nasty area, we check for configuration options, some are required and some arent
    if not hasattr(code.config, 'run_webserver') or not hasattr(code.config, 'webserver_pass'):
        return
    if not code.config.run_webserver:
        return
    if not code.config.webserver_pass:
        print '[ERROR] To use webserver.py you must have a password setup in default.py!'
        return
    Sender = CollectData(code, input, id)
    Sender.start() # Initiate the thread.
    return
initFromIRC.rule = r'.'
initFromIRC.thread = False
initFromIRC.priority = 'low'
initFromIRC.rate = 1

# Initialize the webserver. (Oooooo right!)
thread.start_new_thread(init, (str(host), int(port),))

if __name__ == '__main__':
    print __doc__.strip()