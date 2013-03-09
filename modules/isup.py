#!/usr/bin/env python
"""
Stan-Derp Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
isup.py - Stan-Derp isup Module
http://standerp.liamstanley.net/
"""

import re
import web

def isup(standerp, input):
    """isup.me website status checker"""
    site = input.group(2)
    if not site:
        return standerp.reply("What site do you want to check?")

    if site[:6] != 'http://' and site[:7] != 'https://':
        if '://' in site:
            protocol = site.split('://')[0] + '://'
            return standerp.reply("Try it again without the %s" % protocol)
        else:
            site = 'http://' + site
    try:
        response = web.get(site)
    except Exception as e:
        standerp.say(site + ' looks down from here.')
        return

    if response:
        standerp.say(site + ' looks fine to me.')
    else:
        standerp.say(site + ' is down from here.')
isup.commands = ['isup', 'isitup', 'websiteup', 'ping']
isup.example = ".isup google.com"

if __name__ == '__main__':
    print __doc__.strip()
