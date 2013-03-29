#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
isup.py - Code isup Module
http://code.liamstanley.net/
"""

import re
import web

def isup(code, input):
    """isup.me website status checker"""
    site = input.group(2)
    if not site:
        return code.reply("What site do you want to check?")

    if site[:6] != 'http://' and site[:7] != 'https://':
        if '://' in site:
            protocol = site.split('://')[0] + '://'
            return code.reply("Try it again without the %s" % protocol)
        else:
            site = 'http://' + site
    try:
        response = web.get(site)
    except Exception as e:
        code.say(site + ' looks down from here.')
        return

    if response:
        code.say(site + ' looks fine to me.')
    else:
        code.say(site + ' is down from here.')
isup.commands = ['isup']
isup.example = ".isup google.com"

if __name__ == '__main__':
    print __doc__.strip()
