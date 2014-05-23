from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
import thread
import time
from random import randint as gen
from util import output
import json

# Example command...
#  - http://your-host.net:8888/?pass=herpderptrains&args=PRIVMSG+%23L&data=Testing+123
host = '0.0.0.0'

# Not important
bot, password = None, None


class WebServer(BaseHTTPRequestHandler):
    """The actual webserver that responds to things that received via GET queries."""
    def log_message(self, format, *args):
        msg = '(%s) | [%s] | %s' % (self.address_string(), self.log_date_time_string(), format % args)
        output.info(msg, 'WEBSERVER')

    def do_GET(self):
        def finish(data=''):
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            if isinstance(data, dict):
                data = json.dumps(data, indent=2)
            self.wfile.write(data)
        args = {}
        path = self.path
        if '?' in path:
            tmp = path.split('?', 1)[1]
            args = urlparse.parse_qs(tmp)

            # Manage here
            try:
                if 'pass' not in args:
                    return finish({'success': False, 'message': 'Password required'})
                if args['pass'][0] != password:
                    return finish({'success': False, 'message': 'Password incorrect'})

                # Authenticated.. Now we need to find some variables in the args
                # 1. args (used for IRC commands)
                # 2. data (The argument for the IRC command (the arguments argument!))
                if 'args' not in args or 'data' not in args:
                    config = {}
                    for key, value in bot.config().iteritems():
                        # Add configuration to web-requests, but ensure
                        #  no passwords exists to prevent security issues
                        if not 'pass' in key.lower():
                            config[key] = value
                    data = {
                        'chan_data': bot.chan,
                        'modules': bot.modules,
                        'docs': bot.doc,
                        'config': config
                    }
                    return finish({'success': True, 'data': data})

                bot.write(args['args'][0].split(), bot.format(args['data'][0]))
                return finish({'success': True, 'message': 'Data sent to server'})
            except Exception as e:
                return finish({'success': False, 'message': 'An exception has occured', 'error': str(e)})
        else:
            return finish({'success': False, 'message': 'Password required'})
        finish()


def checkstate(bot, input, id):
    global password
    password = bot.config('webserver_password')

    while True:
        if bot.get('webserver.object') != id:
            return False
        time.sleep(1)


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
    global bot
    bot = code
    id = str(gen(0, 10000000))
    bot.set('webserver.object', id)

    # Nasty area, we check for configuration options, some are required and some arent
    if not bot.config('webserver'):
        return
    if not bot.config('webserver_password'):
        return output.warning('To use the builtin webserver, you must set a password in the config', 'WEBSERVER')
    port = bot.config('webserver_port', 8888)
    thread.start_new_thread(checkstate, (bot, input, id,))
    thread.start_new_thread(init, (str(host), int(port),))
