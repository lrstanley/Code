#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
reload.py - Code Reload Module
http://code.liamstanley.io/
"""

import sys, os.path, time, imp, subprocess
from util.hook import *
from util import output


@hook(cmds=['reload', 'rld'], priority='high', thread=False, admin=True)
def f_reload(code, input):
    """Reloads a module, for use by admins only."""

    name = input.group(2)
    if name == code.config.owner:
        return code.reply('What?')

    if (not name) or (name == '*'):
        code.variables = None
        code.commands = None
        code.setup()
        output.info('Reloaded all modules.')
        return code.reply('{b}Reloaded all modules.')

    # if a user supplies the module with the extension
    if name.endswith('.py'):
        name = os.path.splitext(name)[0]

    if not sys.modules.has_key(name):
        return code.reply('%s: No such module!' % code.bold(name))

    # Thanks to moot for prodding me on this
    path = sys.modules[name].__file__
    if path.endswith('.pyc') or path.endswith('.pyo'):
        path = path[:-1]
    if not os.path.isfile(path):
        return code.reply('Found %s, but not the source file' % code.bold(name))

    module = imp.load_source(name, path)
    sys.modules[name] = module
    if hasattr(module, 'setup'):
        module.setup(code)

    mtime = os.path.getmtime(module.__file__)
    modified = time.strftime('%H:%M:%S', time.gmtime(mtime))

    code.register(vars(module))
    code.bind_commands()
    output.info('Reloaded %s' % module)
    module = str(module)
    module_name, module_location = module.split()[1].strip('\''), module.split()[3].strip('\'').strip('>')
    code.say('{b}Reloaded {blue}%s{c} (from {blue}%s{c}) (version: {blue}%s{c}){b}' % (module_name, module_location, modified))


@hook(cmds=['update'], rate=30, admin=True)
def update(code, input):
    """Pulls the latest versions of all modules from Git"""
    if not sys.platform.startswith('linux'):
        code.say('Warning: %s' % code.bold('Using a non-linux OS, might fail to work!'))
    proc = subprocess.Popen('git pull', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    data = proc.communicate()[0]
    while '  ' in data:
        data = data.replace('  ', ' ')
    code.say('Github: ' + code.bold(data))
    f_reload(code, input)