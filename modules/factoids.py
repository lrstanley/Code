#!/usr/bin/env python
'''
Code Copyright (C) 2012-2014 Liam Stanley
admin.py - Code Admin Module
http://code.liamstanley.io/
'''

import os, string, re
import json
from urllib2 import urlopen
from util.hook import *
from util import database, web


@hook(rule='^\?(.*)$')#.regex(r'^\? ?(.+)')
def factoid(code, input):
    """
        ?<word> -- Shows what data is associated with <word>.
        ? <add|delete|info> [args] -- for management
    """

    # If it's a management command...
    if input.group().startswith('? '):
        if not input.admin:
            return code.reply('{red}You need to be an admin to use that command!')
        return factoid_manage(input.group().split(' ', 1)[1], code, input)

    db = database.get('factoids')

    if len(input.group(1).strip().split()) <= 1:
        id, arguments = input.group(1), ''
    else:
        id, arguments = input.group(1).split(' ', 1)

    if not id in db:
        return code.say('{red}That command doesn\'t exist. (If Admin, add it with "{purple}? add <name> <data>{red}")')

    f = db[id]

    if f.startswith('<py>'):
        data = f[4:].strip()
        variables = 'input="""{}"""; nick="{}"; sender="{}"; bot="{}";'.format(arguments.replace('"', '\\"'),
                                                                                  input.nick, input.sender,
                                                                                  code.nick)
        result = web.pyexec(variables + data, multiline=False)
        return code.say(result)
    elif f.startswith('<act>'):
        result = f[5:].strip()
        return code.action(result)
    elif f.startswith('<url>'):
        url = f[5:].strip()
        try:
            return code.say(urlopen(url).read())
        except:
            return code.say('Failed to fetch the URL.')
    else:
        return code.say(f)


def factoid_manage(data, code, input):
    # This is ugly looking, but I like it built into ? to make it easier to remember commands.
    #   - (Rather than if/fi, af/fa, fr/rf/fd/df)
    if len(data.split()) == 1:
        cmd, args = data, False
    else:
        cmd, args = data.split(' ',1)
    if args:
        name = args.split()[0].lower()
    db = database.get('factoids')
    if cmd.lower() in ['add','create','new']:
        if args:
            if name in db:
                return code.reply('{red}That factoid already exists!')
            else:
                db[name] = args.split(' ',1)[1]
                database.set(db, 'factoids')
                return code.reply('{green}Successfully create the factoid "{purple}%s{green}"!' % name)
        return code.reply(('{red}Use "{purple}? add <name> <args>{red}" to create a new factoid. Use <py>, '
                           '<act>, <url> in front of args for different responses.'))
    elif cmd.lower() in ['del', 'rem', 'delete', 'remove']:
        if args:
            if not name in db:
                return code.reply('{red}That factoid does not exist!')
            else:
                del db[name]
                database.set(db, 'factoids')
                return code.reply('{green}Successfully deleted the factoid "{purple}%s{green}"!' % name)
        return code.reply('{red}Use "{purple}? del <name>{red}" to delete a factoid.')
    elif cmd.lower() == 'info':
        if args:
            if name in db:
                return code.say('Raw: ' + db[name])
            else:
                return code.say('{red}That factoid does not exist!')
        return code.reply('{red}Use "{purple}? info <name>{red}" to view the factoid in raw form.')
    else:
        return code.reply('{red} Usage: "{purple}? <add|delete|info> [args]{red}"')

if __name__ == '__main__':
    print __doc__.strip()
