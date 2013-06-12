#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
fml.py - Code FML Module
http://code.liamstanley.net/
"""

import re
import urllib
import urllib2
import HTMLParser
h = HTMLParser.HTMLParser()

def fml_catch(code, input):
    r = urllib2.urlopen('http://m.fmylife.com/random/').read()# Mobile version, as it loads faster
    r = r.replace('\t', '').replace('\r', '').replace('\n', '').decode('utf-8')
    response = r.split('<p class="text">', 1)[1].split('</p>', 1)[0]
    isfml = r.split('sucks</a> <strong>', 1)[1].split('</strong>', 1)[0].strip()
    notfml = r.split('it</a> <strong>', 1)[1].split('</strong>', 1)[0].strip()
    response = re.sub(r'\<.*?\>', '', response).strip()
    if len(response) > 490: return code.say(response) # getting too long: ignore isfml/isnot
    response = h.unescape('%s +%s/-%s' % (response, code.bold(isfml), code.bold(notfml)))
    code.say(response)
fml_catch.commands = ['fml']
fml_catch.example = '.fml'
fml_catch.rate = 20


if __name__ == '__main__':
    print __doc__.strip()
