import sys
import os
import time
import imp
import re
import subprocess
from util.hook import *
from util import output
from core.bind import bind_commands


def reload_all_modules(code):
    code.variables = None
    code.commands = None
    code.setup()
    output.info('Reloaded all modules')


def reload_module(code, name):
    name = name.strip('.py')
    if name not in sys.modules:
        return 1
    path = sys.modules[name].__file__
    if path.endswith('.pyc') or path.endswith('.pyo'):
        path = path[:-1]
    module = imp.load_source(name, path)
    sys.modules[name] = module
    if hasattr(module, 'setup'):
        module.setup(code)
    code.register(vars(module))
    bind_commands(code)
    mtime = os.path.getmtime(module.__file__)
    modified = time.strftime('%H:%M:%S', time.gmtime(mtime))
    module = str(module)
    module_name, module_location = module.split()[1].strip(
        '\''), module.split()[3].strip('\'').strip('>')
    output.info('Reloaded %s' % module)
    return {
        'name': module_name,
        'location': module_location,
        'time': modified
    }


@hook(cmds=['unload', 'unloadmodule', 'unloadmod'], args=True, priority='high', admin=True)
def unload_module(code, input):
    name = input.group(2)
    home = os.getcwd()
    name = name.strip('.py')
    # Get all files in modules directory
    tmp = os.listdir(os.path.join(home, 'modules'))
    modules = []
    for module in tmp:
        if module.endswith('.pyc'):
            continue
        module = module.strip('.py')
        modules.append(module)
    if name not in modules:
        return code.say('That module doesn\'t exist!')
    if name in code.unload:
        return code.say('It seems that module has already been set to say unloaded!')
    if name in code.load:
        # Remove from unload, and add to load
        del code.load[code.load.index(name)]
    filename = os.path.join(home, 'modules', name + '.py')
    code.unload.append(name)
    code.say('{b}Unloaded %s!' % name)
    reload_all_modules(code)
    code.say('{b}Reloaded all modules')


@hook(cmds=['load', 'loadmodule', 'loadmod'], args=True, priority='high', admin=True)
def load_module(code, input):
    name = input.group(2)
    home = os.getcwd()
    name = name.strip('.py')
    # Get all files in modules directory
    tmp = os.listdir(os.path.join(home, 'modules'))
    modules = []
    for module in tmp:
        if module.endswith('.pyc'):
            continue
        module = module.strip('.py')
        modules.append(module)
    if name not in modules:
        return code.say('{b}That module doesn\'t exist!')
    if name in code.modules:
        return code.say('{b}That module seems to be already loaded!')
    if name in code.load:
        return code.say('{b}It seems that module has already been set to load!')
    if name in code.unload:
        # Remove from unload, and add to load
        del code.unload[code.unload.index(name)]
    # Try and load here. If it doesn't work, make sure it's not in code.load, and output error
    # If it works, add to code.load
    filename = os.path.join(home, 'modules', name + '.py')
    try:
        code.setup_module(name, filename, is_startup=False)
    except Exception as e:
        return code.say('{red}Error{c}: %s' % str(e))
    code.load.append(name)
    return code.say('{b}Loaded %s!' % name)


@hook(cmds=['reload', 'rld'], priority='high', thread=False, admin=True)
def f_reload(code, input):
    """Reloads a module, for use by admins only."""

    name = input.group(2)

    if not name or name == '*':
        reload_all_modules(code)
        return code.reply('{b}Reloaded all modules.')

    try:
        module = reload_module(code, name)
    except Exception as e:
        code.say('Error reloading %s: %s' % (name, str(e)))
    if module == 1:
        return code.reply('The module {b}%s{b} isn\'t loaded! use %sload <module>' % (name, code.prefix))
    code.say(
        '{b}Reloaded {blue}%s{c} (from {blue}%s{c}) (version: {blue}%s{c}){b}' %
        (module['name'], module['location'], module['time']))


@hook(cmds=['update'], rate=20, admin=True)
def update(code, input):
    """Pulls the latest versions of all modules from Git"""
    if not sys.platform.startswith('linux'):
        output.warning('Warning: {b}Using a non-unix OS, might fail to work!')
    try:
        proc = subprocess.Popen(
            'git pull', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        git_data = proc.communicate()[0]
    except:
        return code.say('Either Git isn\'t installed or there was an error! (Using Windows?)')
    if git_data.strip('\n') == 'Already up-to-date.':
        return code.say('{b}No updates found.')
    data = git_data
    if re.match(r'^Updating [a-z0-9]{7}\.\.[a-z0-9]{7}$', data.strip('\n')):
        # Pretty sure files are conflicting...
        return code.say('{b}Files are conflicting with the update. Please refork the bot!')
    # per-file additions/subtractions that spam stuff
    data = re.sub(r'[0-9]+ [\+\-]+', '', data).replace('\n', ' ')
    # mode changes, as those are unimportant
    data = re.sub(r'create mode [0-9]+ [a-zA-Z0-9\/\\]+\.py', '', data)
    # commit hashes, different color
    data = re.sub(
        r'(?P<first>[a-z0-9]{7})\.\.(?P<second>[a-z0-9]{7})', '{purple}\g<first>..\g<second>{c}', data)
    # make different files depending on the importance
    data = re.sub(
        r'core/modules/(?P<name>[a-zA-Z0-9]+)\.py', '\g<name>.py ({red}core{c})', data)
    data = re.sub(
        r'core/(?P<name>[a-zA-Z0-9]+)\.py', '\g<name>.py ({red}core{c})', data)
    data = re.sub(r'code\.py', 'code.py ({red}base{c})', data)
    data = re.sub(
        r'modules/(?P<name>[a-zA-Z0-9]+)\.py', '\g<name>.py ({blue}module{c})', data)
    data = re.sub(
        r'util/(?P<name>[a-zA-Z0-9]+)\.py', '\g<name>.py ({pink}util{c})', data)
    data = re.sub(r'lib/(?P<dir>[a-zA-Z0-9]+)/(?P<name>[a-zA-Z0-9]+)\.py',
                  '\g<name>.py ({pink}\g<dir> - util{c})', data)

    data = data.replace('Fast-forward', '')
    # Do a little with file changes
    data = re.sub(
        r'(?P<files>[0-9]{1,3}) files? changed', '{green}\g<files>{c} files changed', data)
    data = re.sub(r'(?P<ins>[0-9]{1,6}) insertions\(\+\)\, (?P<dels>[0-9]{1,6}) deletions\(\-\)',
                  '+{green}\g<ins>{c}/-{red}\g<dels>{c}', data)
    data = re.sub(
        r'(?P<chars>[0-9]{1,6}) insertions\(\+\)', '{green}\g<chars>{c} additions', data)
    data = re.sub(
        r'(?P<chars>[0-9]{1,6}) deletions\(\+\)', '{green}\g<chars>{c} deletions', data)
    while '  ' in data:
        data = data.replace('  ', ' ')
    code.say('Github: {b}' + data.strip())
    core_stuff = ['code.py', 'core/', 'util/', 'lib/']
    for item in core_stuff:
        if item.lower() in git_data.lower().strip('\n'):
            code.say(
                '{b}{red}Core files have been edited, restarting the bot!{c}')
            return code.restart()
    reload_all_modules(code)
    code.say('{b}Reloaded all modules')
