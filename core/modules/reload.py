import sys
import os.path
import time
import imp
import subprocess
from util.hook import *
from util import output


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
    code.bind_commands()
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
        code.say('Warning: {b}Using a non-linux OS, might fail to work!')
    proc = subprocess.Popen(
        'git pull', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    data = proc.communicate()[0]
    while '  ' in data:
        data = data.replace('  ', ' ')
    code.say('Github: {b}' + data)
    reload_all_modules(code)
