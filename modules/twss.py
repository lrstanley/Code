#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
twss.py - Code 'That's what she said' Module
http://code.liamstanley.io/
"""


import urllib
import socket
import re
import os
from util.hook import *


socket.setdefaulttimeout(5)

last = "DEBUG_ME"  # Dont find this in terminal, you might want to flip shit.
if not os.path.exists('modules/twss.db'):
    print '[DOWNLOADING] "That\'s What She Said" library from http://misc.liamstanley.io/twss.txt'
    urllib.urlretrieve('http://misc.liamstanley.io/twss.txt', 'modules/twss.db')

    f = open('modules/twss.db', 'w')


@hook(rule=r'(.*)', priority='low')
def say_it(code, input):
    global last
    user_quotes = None
    with open('modules/twss.db') as f:
        scraped_quotes = frozenset([line.rstrip() for line in f])
    if os.path.exists('modules/twss_ua.db'):
        with open('modules/twss_ua.db') as f2:
            user_quotes = frozenset([line.rstrip() for line in f2])
    quotes = scraped_quotes.union(user_quotes) if user_quotes else scraped_quotes
    formatted = input.group(1).lower()
    if re.sub('[^\w\s]', '', formatted) in quotes:
        code.say('That\'s what she said.')
    last = re.sub('[^\w\s]', '', formatted)


@hook(cmds=['twss'], priority='low', thread=False, admin=True)
def add_twss(code, input):
    if len(last) < 5:
        return
    print last
    with open('modules/twss_ua.db', 'a') as f:
        f.write(re.sub(r'[^\w\s]', '', last.lower()) + '\n')
        f.close()
    code.say('That\'s what she said.')
