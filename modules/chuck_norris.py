#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
chuck_norris.py - Code Chuck Norris Module
http://code.liamstanley.net/
"""

import json
import urllib2
import HTMLParser
h = HTMLParser.HTMLParser()

def chuck(code, input):
    try:
        r = urllib2.urlopen('http://api.icndb.com/jokes/random').read()
    except:
        return code.say('Chuck seems to be in the way. I\'m not fucking with him.')
    data = json.loads(r)
    code.say('#%s - %s' % (
                           code.color('blue',data['value']['id']),
                           h.unescape(data['value']['joke'])
                           ))
chuck.commands = ['chuck','norris','cn','chucknorris']
chuck.example = '.chuck'
chuck.rate = 10

if __name__ == '__main__':
    print __doc__.strip()
