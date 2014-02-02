#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich, andrix: https://gist.github.com/andrix/1423960
isup.py - Code isup Module
http://code.liamstanley.io/
"""

import re
from urllib import urlopen
import string

def isup(code,input):
    """Is it down for everyone, or just me?"""
    synerr = input.nick + ': The syntax is \'.isup <uri>\' e.g, \'.isup http://google.com\''
    try:
        if not input.group(2): return code.reply('Please enter an input.')
        domain = input.group(2)
        chars = set('~`!@$%^&*()+=[]{}|;,<>?')
        if not domain.find('.') > -1:
            code.say(synerr)
            return
        else:
            splituri = domain.split('.')
            splitrev = splituri[::-1]
            if len(splitrev[0]) > 4 or len(splitrev[1]) > 63 or any((c in chars) for c in domain): #<3 Tomko
                code.say(input.nick + ': ' + code.color('red', 'You have specified an incorrect %s.') % (code.bold('URI')))
                return
            else:
                pass
        resp = urlopen('http://www.isup.me/%s' % domain).read()
        up = code.color('lime', 'Looks like it\'s up from here, %s just be you! %s') % (code.italic( 'must'), code.bold(':('))
        down = code.color('red', 'Looks like it\'s down from here too! %s') % (code.bold(':O'))
        response = '%s: %s' % (input.nick, up if re.search('It\'s just you.', resp, re.DOTALL) else down)
        if response.find('NONE') > -1:
            code.say(synerr)
            return
        else:
            code.say(response)
    except:
        code.say(synerr)

isup.commands = ['isup', 'isdown', 'check', 'up', 'down']
isup.example = '.isup http://google.com'

if __name__ == '__main__':
    print __doc__.strip()
