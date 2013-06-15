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

def fml(code, input):
    r = urllib2.urlopen('http://m.fmylife.com/random/').read()# Mobile version, as it loads faster
    r = r.replace('\t', '').replace('\r', '').replace('\n', '').decode('utf-8')
    fml = re.compile(r'<p class="text">.*?</p>').findall(r)
    fml_lvl = re.compile(r'</a> <strong>.*?</strong>').findall(r)
    fml = re.sub(r'\<.*?\>', '', fml[0]).strip().rstrip(' FML')
    isfml = re.sub(r'\<.*?\>', '', fml_lvl[0]).strip()
    notfml = re.sub(r'\<.*?\>', '', fml_lvl[1]).strip()
    if len(fml) > 490: return code.say(h.unescape(fml)) # getting too long: ignore isfml/isnot
    code.say(h.unescape('%s %s +%s/-%s' % (fml, code.color('red', 'FML'), code.bold(isfml), code.bold(notfml))))
fml.commands = ['fml']
fml.example = '.fml'
fml.rate = 20


if __name__ == '__main__':
    print __doc__.strip()
