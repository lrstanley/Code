import sys
import os
import time
import imp
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
        raise Exception('NoSuchModule', 'Module doesnt exist!')
    path = sys.modules[name].__file__
    if path.endswith('.pyc') or path.endswith('.pyo'):
        path = path[:-1]
    if not os.path.isfile(path):
        raise Exception(
            'NoSuchFile', 'Found the compiled code, but not the module!')
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
    if name in code.unload: # <------------ TEST!
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

    if (not name) or (name == '*'):
        reload_all_modules(code)
        return code.reply('{b}Reloaded all modules.')

    try:
        module = reload_module(code, name)
    except NoSuchModule:
        return code.reply('{b}%s{b}: No such module!' % name)
    except NoSuchFile:
        return code.reply('{b}Found the compiled code, but not the module!')
    code.say(
        '{b}Reloaded {blue}%s{c} (from {blue}%s{c}) (version: {blue}%s{c}){b}' %
        (module['name'], module['location'], module['time']))


@hook(cmds=['update'], rate=30, admin=True)
def update(code, input):
    """Pulls the latest versions of all modules from Git"""
    if not sys.platform.startswith('linux'):
        code.say('Warning: {b}Using a non-unix OS, might fail to work!')
    proc = subprocess.Popen(
        'git pull', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    data = proc.communicate()[0]
    while '  ' in data:
        data = data.replace('  ', ' ')
    code.say('Github: {b}' + data)
    reload_all_modules(code)
    code.say('{b}Reloaded all modules')