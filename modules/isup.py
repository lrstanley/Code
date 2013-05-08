#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich, andrix: https://gist.github.com/andrix/1423960
isup.py - Code isup Module
http://code.liamstanley.net/
"""

import re
from urllib import urlopen

def isup(code,input):
    """Is it down for everyone, or just me?"""
    synerr = input.nick + ': The syntax is \'.isup <uri>\' e.g, \'.isup http://google.com\''
    try:
        domain = input.group(2)
        if not domain.find('.') > -1:
            code.say(synerr)
            return
        resp = urlopen('http://www.isup.me/%s' % domain).read()
        response = '%s: %s' % (input.nick, code.color('lime', 'Looks up from here, must just be you! :(') if re.search('It\'s just you.', resp, re.DOTALL) else code.color('red', 'Looks like it\'s down from here too! :o'))
        if response.find('NONE') > -1:
            code.say(synerr)
            return
        else:
            code.say(response)
    except:
        code.say(synerr)

isup.commands = ['isup', 'check', 'ping']
isup.example = '.isup http://google.com'

if __name__ == '__main__':
    print __doc__.strip()
