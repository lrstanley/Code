from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
import thread
import time
from random import randint as gen
from util import output
import json
import os
from util.tools import hrt
from core.modules import load as reload

# Some todo lists...
# - As suggested by Allen, might add a public API that allows basic non-security-issue data to be given
# - About dialog and information
# - Some form of graphing system, so that the logs aren't on the main page


# Example command...
#  - http://your-host.net:8888/?pass=herpderptrains&args=PRIVMSG+%23L&data=Testing+123
host = '0.0.0.0'

# Not important
bot, password = None, None


class WebServer(BaseHTTPRequestHandler):

    """
        The actual webserver that responds to things that received via GET queries.
        Other modules can add data to the JSON API, via:
         - code.webserver_data['your_data_variable'] = ['this', 'is', 'a', 'list']
        It can be accessed via the ['other']['your_data_variable'] data attribute via the API.
    """

    def log_message(self, format, *args):
        pass
        # msg = '(%s) | [%s] | %s' % (self.address_string(), self.log_date_time_string(), format % args)
        # output.info(msg, 'WEBSERVER')

    def do_GET(self):
        init_time = float(time.time())

        def readfile(fn):
            if not os.path.isfile('webserver/%s' % fn):
                return False
            try:
                with open('webserver/%s' % fn, 'r') as f:
                    return f.read()
            except:
                return False

        def finish(data='', content='application/json', code=200):
            self.send_response(code)
            self.send_header("Content-type", content)
            self.end_headers()
            done = float(time.time()) - init_time
            if bot.debug:
                output.info('Finished request for %s (took %f seconds)' % (self.path, done), 'WEBSERVER')
            if isinstance(data, dict):
                data = json.dumps(data, indent=2)
            self.wfile.write(data)

        args = {}
        if bot.debug:
            output.warning('Request for "%s" (%s)' % (self.path, ', '.join([self.command, self.request_version, list(self.client_address)[0]])), 'WEBSERVER')
        path = self.path.replace('?callback=?', '')
        if path.startswith('/?'):
            tmp = path.split('?', 1)[1]
            args = urlparse.parse_qs(tmp)

            # Manage here
            try:
                if 'pass' not in args:
                    return finish({'success': False, 'message': 'Password required. Example: http://localhost:8888/?pass=mypassword'}, code=403)
                if args['pass'][0] != password:
                    return finish({'success': False, 'message': 'Password incorrect'}, code=403)

                # Authenticated.. Now we need to find some variables in the args
                # 1. args (used for IRC commands)
                # 2. data (The argument for the IRC command (the arguments
                # argument!))
                if 'execute' in args:
                    cmd = args['execute'][0]
                    if cmd == 'mute':
                        bot.mute()
                    if cmd == 'unmute':
                        bot.unmute()
                    if cmd == 'restart':
                        bot.restart()
                    if cmd == 'quit':
                        bot.quit()
                    if cmd == 'reloadall':
                        reload.reload_all_modules(bot)
                        return finish({'success': True, 'message': 'Reloaded all modules!'})
                    if cmd == 'reload':
                        tmp = reload.reload_module(bot, args['data'][0])
                        return finish({'success': True, 'message': 'Reloaded %s!' % tmp['name']})
                if 'args' not in args:
                    config = {}
                    for key, value in bot.config().iteritems():
                        # Add configuration to web-requests, but ensure
                        #  no passwords exists to prevent security issues
                        if 'pass' not in key.lower():
                            config[key] = value
                    data = {
                        'nick': bot.nick,
                        'chan_data': bot.chan,
                        'modules': sorted(bot.modules),
                        'docs': bot.doc,
                        'config': config,
                        'bot_startup': hrt(bot.bot_startup)[0],
                        'irc_startup': hrt(bot.irc_startup)[0],
                        'muted': bot.muted,
                        'other': bot.webserver_data,
                        'server': bot.server_options,
                        'logs1': bot.logs,
                        'bans': bot.bans
                    }
                    data['logs'] = []
                    for log in bot.logs['bot']:
                        tmp = log
                        tmp['hrt'] = hrt(tmp['time'])[0]
                        data['logs'].append(tmp)
                    return finish({'success': True, 'data': data})

                if 'data' in args:
                    bot.write(
                        args['args'][0].split(), bot.format(args['data'][0]))
                else:
                    bot.write(args['args'][0].split())
                return finish({'success': True, 'message': 'Data sent to server'})
            except Exception as e:
                return finish({'success': False, 'message': 'An exception has occured', 'error': list(e)}, code=500)
        elif path.endswith('/'):
            target = path + 'index.html'
            filetype = 'text/html'
        else:
            target = path
            if '.' in path:
                filetype = 'text/' + path.split('.')[-1]
            else:
                filetype = 'text/html'
        if filetype == 'text/js':
            filetype = 'application/javascript'
        f = readfile(target.strip('/'))
        if not f:
            return finish('404 file now found', content='text/html', code=400)
        return finish(f, content=filetype, code=200)


def checkstate(bot, input, id):
    global password
    password = bot.config('webserver_password')

    while True:
        if bot.debug:
            output.info('Running check to see if the webserver needs to be restarted', 'WEBSERVER')
        if bot.get('webserver.object') != id:
            return False
        time.sleep(1)


def init(host, port):
    """Tries to start the webserver. Fails if someone initiates a reload, or port is already in use."""
    try:
        time.sleep(5)
        server = HTTPServer(('0.0.0.0', port), WebServer)
        output.success('Starting HTTP server on %s:%s' %
                       (host, port), 'WEBSERVER')
    except:
        return
    server.serve_forever()


def setup(code):
    global bot
    bot = code
    id = str(gen(0, 10000000))
    bot.set('webserver.object', id)

    # Nasty area, we check for configuration options, some are required and
    # some arent
    if not bot.config('webserver'):
        return
    if not bot.config('webserver_password'):
        return output.warning('To use the builtin webserver, you must set a password in the config', 'WEBSERVER')
    port = bot.config('webserver_port', 8888)
    if bot.debug:
        output.info('Running daemon', 'WEBSERVER')
    thread.start_new_thread(checkstate, (bot, input, id,))
    thread.start_new_thread(init, (str(host), int(port),))
