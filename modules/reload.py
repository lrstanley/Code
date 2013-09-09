#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
reload.py - Code Module Reloader Module
http://code.liamstanley.net/
"""

import sys, os.path, time, imp, subprocess
import irc

def f_reload_cmd(code, input):
    f_reload(code, input)
f_reload_cmd.commands = ['rld', 'reload', 'recompile']

def f_reload(code, input): 
    """Reloads a module, for use by admins only.""" 
    if not input.admin: return

    name = input.group(2)
    if name == code.config.owner: 
        return code.reply('What?')

    if (not name) or (name == '*'): 
        code.variables = None
        code.commands = None
        code.setup()
        return code.reply(code.bold('Reloaded all modules.'))

    # if a user supplies the module with the extension
    if name.endswith('.py'):
        name = os.path.splitext(name)[0]

    if not sys.modules.has_key(name): 
        return code.reply('%s: no such module!' % code.bold(name))

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
    modified = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(mtime))

    code.register(vars(module))
    code.bind_commands()

    code.reply('%r (version: %s)' % (module, modified)) # no colorcodes, weird shit happens!
f_reload.name = 'reload'
f_reload.rule = ('$nick', ['reload'], r'(\S+)?')
f_reload.priority = 'low'
f_reload.thread = False
f_reload.rate = 20


if sys.version_info >= (2, 7):
    def update(code, input):
        if not input.admin:
              return

        """Pulls the latest versions of all modules from Git"""
        if not sys.platform.startswith('linux'):
            return code.reply('This form of update is only supported if you\'re running linux')
        proc = subprocess.Popen('/usr/bin/git pull',
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, shell=True)
        data = proc.communicate()[0]
        while '  ' in data:
            data = data.replace('  ', ' ')
        code.say('Github: ' + code.bold(data))
        f_reload(code, input)
else:
    def update(code, input):
        code.reply('You need to run me on %s to do that.' % code.bold(code.color('red', 'Python 2.7')))
#update.rule = ('$nick', ['update'], r'(.+)')
update.commands = ['update']
update.rate = 30

if __name__ == '__main__': 
    print __doc__.strip()
