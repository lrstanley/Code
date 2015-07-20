from util import output
import threading
from util.tools import hrt
import datetime
import hashlib
import os
import functools
from core.modules import load as reload
from lib.bottle import TEMPLATE_PATH, route, get, post, run, request, response, redirect, static_file, jinja2_template as template

host = '0.0.0.0'
fmt = '%H:%M:%S'

# Not important
bot = None


# Authentication methods:
# * http://<hostname>:<port>/<query>?auth=sha256_hashed_password
# * http://<hostname>:<port>/<query> (using "auth" within post data)
# * http://<hostname>:<port>/<query> (using "auth" within application/json data)
#
#
# Possible queries:
# * Moreso execution-based stuff:
#   * [POST] http://<hostname>:<port>/exec
#   * [POST] http://<hostname>:<port>/exec/<query>
#   * [POST] http://<hostname>:<port>/exec/<query>/<sub-query>
#
# * Informational queries:
#   * [GET]  http://<hostname>:<port>/api
#   * [GET]  http://<hostname>:<port>/api/<list-of-args-separated-by-comma>
#
# Wish to add data to the API from a module? Simply use:
# code.webserver_data["your_key"] = {'your': data}
#
#   NOTE: The above can be accessed with "http://<hostname>:<port>/api/other".
#   "other" is a dictionary of data from other possible modules.
#
# Other things to note:
#
#  * Successful and failed logins are logged to console
#  * Requests to "/" are logged, as a general "access" notification
#  * All "/exec*" queries are logged for safety reasons


TEMPLATE_PATH[:] = ['./core/webserver']


def verify(key, raw=False):
    hashkey = str(hashlib.sha256(bot.config('webserver_password')).hexdigest())
    if raw:
        if key == bot.config('webserver_password'):
            return hashkey
        else:
            return False
    if key == hashkey:
        return True
    else:
        return False


def login_required(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        if verify(request.cookies.auth):
            return method(*args, **kwargs)
        elif verify(request.forms.auth):
            return method(*args, **kwargs)
        elif verify(request.query.auth):
            return method(*args, **kwargs)
        else:
            # do login
            return redirect("/login")
    return wrapper


@route('/')
@login_required
def index():
    output.warning("Webpanel access from %s" % request.remote_addr, "WEBSERVER")
    return template('index.html')


@route('/static/:filename#.*#')
def send_static(filename):
    return static_file(filename, root='./core/webserver')


@get('/login')
def login():
    if verify(request.cookies.auth):
        return redirect('/')
    return template('login.html')


@post('/login')
def login_auth():
    bad = "Failed login from %s" % request.remote_addr
    good = "Successful login from %s" % request.remote_addr
    if request.json:
        post_data = request.json
    else:
        post_data = request.forms
    if not post_data:
        output.error(bad, "WEBSERVER")
        return {'success': False}

    isauthed = verify(post_data['passwd'], raw=True)
    if isauthed:
        response.set_cookie("auth", isauthed, max_age=2419200, path="/")
        output.success(good, "WEBSERVER")
        return {'success': True}
    else:
        output.error(bad, "WEBSERVER")
        return {'success': False}


@route('/logout')
def logout():
    response.delete_cookie("auth", path="/")
    return redirect("/login")


@post('/exec')
@login_required
def raw_exec():
    if request.json:
        # Using application/json headers
        post_data = request.json
    else:
        # Using form or x-www-form-urlencoded headers
        post_data = request.forms
    if not post_data:
        return {'success': False}

    try:
        if "args" in post_data and "data" in post_data:
            output.warning("Execution from webpanel: [%s] [%s]" % (str(post_data['args']), str(post_data['data'])), "WEBSERVER")
            bot.write(post_data['args'].split(), bot.format(post_data['data']))
            return {'success': True}
        elif "args" in post_data:
            output.warning("Execution from webpanel: [%s]" % str(post_data['args']), "WEBSERVER")
            bot.write(post_data['args'].split())
            return {'success': True}
        else:
            return {'success': False}
    except:
        return {'success': False}


@route('/exec/reload')
@route('/exec/reload/<name>')
@login_required
def mod_reload(name=None):
    if not name:
        output.warning("Execution from webpanel: Reload all modules", "WEBSERVER")
        reload.reload_all_modules(bot)
        return {'reload': True}
    else:
        output.warning("Execution from webpanel: Reload module %s" % str(name), "WEBSERVER")
        reload.reload_module(bot, str(name))
        return {'reload': True}


@route('/exec/unload/<name>')
@login_required
def mod_unload(name):
    home = os.getcwd()
    name = name.strip('.py')
    # Get all files in modules directory
    tmp = os.listdir(os.path.join(home, 'modules'))
    modules = []
    for module in tmp:
        if module.endswith('.pyc'):
            continue
        module = module.replace('.py', '')
        modules.append(module)
    if name not in modules:
        return {'success': False, 'message': 'That module doesn\'t exist'}
    if name in bot.unload:
        return {'success': False, 'message': 'Module already unloaded'}
    if name in bot.load:
        # Remove from load, and add to unload
        del bot.load[bot.load.index(name)]
    output.warning("Execution from webpanel: Unload module %s" % str(name), "WEBSERVER")
    bot.unload.append(name)
    reload.reload_all_modules(bot)
    return {'success': True}


@route('/exec/load/<name>')
@login_required
def mod_load(name):
    home = os.getcwd()
    name = name.replace('.py', '')
    # Get all files in modules directory
    tmp = os.listdir(os.path.join(home, 'modules'))
    modules = []
    for module in tmp:
        if module.endswith('.pyc'):
            continue
        module = module.replace('.py', '')
        modules.append(module)
    if name not in modules:
        return {'success': False, 'message': 'Module doesn\'t exist'}
    if name in bot.modules:
        return {'success': False, 'message': 'Module already loaded'}
    if name in bot.load:
        return {'success': False, 'message': 'Module already set to load'}
    if name in bot.unload:
        # Remove from unload, and add to load
        del bot.unload[bot.unload.index(name)]
    # Try and load here. If it doesn't work, make sure it's not in bot.load, and output error
    # If it works, add to bot.load
    filename = os.path.join(home, 'modules', name + '.py')
    try:
        bot.setup_module(name, filename, is_startup=False)
    except Exception as e:
        return {'success': False, 'message': 'Exception: ' + str(e)}
    output.warning("Execution from webpanel: Load module %s" % str(name), "WEBSERVER")
    bot.load.append(name)
    return {'success': True}


@route('/exec/restart')
@login_required
def restart():
    output.warning("Execution from webpanel: Restart bot", "WEBSERVER")
    bot.restart()


@route('/exec/shutdown')
@login_required
def shutdown():
    output.warning("Execution from webpanel: Shutdown bot", "WEBSERVER")
    bot.quit()


@route('/exec/mute')
@login_required
def mute():
    output.warning("Execution from webpanel: Mute bot", "WEBSERVER")
    bot.mute()
    return {'muted': True}


@route('/exec/unmute')
@login_required
def unmute():
    output.warning("Execution from webpanel: Unmute bot", "WEBSERVER")
    bot.unmute()
    return {'muted': False}


@route('/api')
@route('/api/<name>')
@login_required
def api(name=None):
    config = {}
    try:
        for key, value in bot.config().iteritems():
            # Add configuration to web-requests, but ensure
            #  no passwords exists to prevent security issues
            if 'pass' not in key.lower():
                config[key] = value
        data = {
            'nick': bot.nick,
            'chan_data': bot.chan,
            'channels': bot.chan.keys(),
            'modules': sorted(bot.modules),
            'docs': bot.doc,
            'config': config,
            'bot_startup': hrt(bot.bot_startup)[0],
            'irc_startup': hrt(bot.irc_startup)[0],
            'muted': bot.muted,
            # bot.webserver_data allows any plugin to add data to the api
            'other': bot.webserver_data,
            'server': bot.server_options,
            'logs_all': bot.logs,
            'bans': bot.bans
        }
        data['logs'] = []
        for log in bot.logs['bot']:
            tmp = log
            tmp['timestamp'] = datetime.datetime.fromtimestamp(float(tmp['time'])).strftime(fmt)
            data['logs'].append(tmp)

        if name and name != 'all':
            if ',' in name:
                try:
                    names = list(name.replace(' ', '').split(','))
                    tmp = {}
                    for item in names:
                        if item in names:
                            tmp[item] = data[item]
                    return tmp
                except:
                    return {}
            else:
                try:
                    return {name: data[name]}
                except:
                    return {}
        return data
    except:
        return {}


def daemon():
    try:
        port = bot.config('webserver_port', 8888)
        output.info('Starting server [%s] [%s]' % (host, str(port)), 'WEBSERVER')
        run(host=host, port=int(port), quiet=True)
    except Exception as e:
        if bot.debug:
            output.error(str(e), "WEBSERVER")


def setup(code):
    global bot
    bot = code

    if not bot.config('webserver'):
        return
    if not bot.config('webserver_password'):
        return output.warning('To use the builtin webserver, you must set a password in the config', 'WEBSERVER')
    try:
        threading.Thread(target=daemon, kwargs=dict()).start()
    except:
        return
