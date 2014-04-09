#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
seen.py - Code Seen Module
http://code.liamstanley.io/
"""

import time
from util.hook import *


@hook(cmds=['seen'], args=True)
def seen(code, input):
    """seen <nick> - Reports when <nick> was last seen."""
    nick = input.group(2)
    nick = nick.lower()
    if not hasattr(code, 'seen'):
        return code.reply("?")

    if nick in code.seen:
        channel, t = code.seen[nick]
        t = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(t))

        msg = "I last saw {blue}%s{c} at {b}%s{b} on {b}%s{b}" % (nick, t, channel)
        code.reply(msg)
    else:
        code.reply('Sorry, I haven\'t seen %s around.' % code.color('blue', nick))


@deprecated
def f_note(self, origin, match, args):
    def note(self, origin, match, args):
        if not hasattr(self.bot, 'seen'):
            self.bot.seen = {}
        if origin.sender.startswith('#'):
            self.seen[origin.nick.lower()] = (origin.sender, time.time())

    try:
        note(self, origin, match, args)
    except Exception, e:
        print e
f_note.rule = r'(.*)'
f_note.priority = 'low'
