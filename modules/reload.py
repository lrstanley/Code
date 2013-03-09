#!/usr/bin/env python
"""
Stan-Derp Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
reload.py - Stan-Derp Module Reloader Module
http://standerp.liamstanley.net/
"""

import sys, os.path, time, imp
import irc

def f_reload(standerp, input): 
   """Reloads a module, for use by admins only.""" 
   if not input.admin: return

   name = input.group(2)
   if name == standerp.config.owner: 
      return standerp.reply('What?')

   if (not name) or (name == '*'): 
      standerp.variables = None
      standerp.commands = None
      standerp.setup()
      return standerp.reply('done')

   if not sys.modules.has_key(name): 
      return standerp.reply('%s: no such module!' % name)

   # Thanks to moot for prodding me on this
   path = sys.modules[name].__file__
   if path.endswith('.pyc') or path.endswith('.pyo'): 
      path = path[:-1]
   if not os.path.isfile(path): 
      return standerp.reply('Found %s, but not the source file' % name)

   module = imp.load_source(name, path)
   sys.modules[name] = module
   if hasattr(module, 'setup'): 
      module.setup(standerp)

   mtime = os.path.getmtime(module.__file__)
   modified = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(mtime))

   standerp.register(vars(module))
   standerp.bind_commands()

   standerp.reply('%r (version: %s)' % (module, modified))
f_reload.name = 'reload'
f_reload.rule = ('$nick', ['reload'], r'(\S+)?')
f_reload.priority = 'low'
f_reload.thread = False

if __name__ == '__main__': 
   print __doc__.strip()
