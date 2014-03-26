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
import util.web


@hook(rule='^\?(.*)$')#.regex(r'^\? ?(.+)')
def factoid(code, input):
    """
        ?<word> -- Shows what data is associated with <word>.
        ? <add|delete|info> [args] -- for management
    """
    print repr(input.group())

    # If it's a management command...
    if input.group().startswith('? '):
        factoid_manage(input.group().split(' ', 1)[1], code, input)

    db = code.get('factoids')
    if not db:
        db = {}
        code.set('factoids', {})

    if len(input.group().strip().split()) == 1:
        id, arguments = input.group(), ''
    else:
        id, arguments = input.group().split(' ', 1)

    if not id in db:
        return code.say('{red}That command doesn\'t exist. (If Admin, add it with "{purple}? add <name> <data>{c}{c}"')

    f = db[id]

    if f.startswith('<py>'):
        arguments = f[4:].strip()
        variables = 'input="""{}"""; nick="{}"; sender="{}"; bot="{}";'.format(arguments.replace('"', '\\"'),
                                                                                  input.nick, input.sender,
                                                                                  code.nick)
        result = util.web.pyexec(variables + arguments, multiline=False)
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
    print 'derp'