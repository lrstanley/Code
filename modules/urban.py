#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
minecraft.py - Code Urban Dictionary Module
http://code.liamstanley.net/
"""

import urllib2
import re
import HTMLParser

h = HTMLParser.HTMLParser()
# this is really crappy, due to manually parsing html, but it's better than using oblique.
# will clean up at a later time
def urban(code, input):
    if not input.group(2): return code.reply(code.color('red', 'Please enter an input.'))
    uri = 'http://www.urbandictionary.com/define.php?term=%s'
    word = input.group(2).lower()
    word = re.sub(r'[^\w\s]', '+', word)
    word = word.replace('.', '+')
    word = word.replace(' ', '+')
    while word.find('++') > -1:
        word = word.replace('++', '+')
        word = word.strip('+')
    try:
        response = urllib2.urlopen(uri % (word))
        response = response.read().replace("\t", " ").replace("\r", " ").replace("\n", " ")
    except urllib2.HTTPError as e:
        return code.reply(code.color('red', 'urbandictionary.com did not respond correctly, is it down?'))
    response = response.split('<div class="definition">', 1)
    try: response = response[1]
    except: return code.say('I\'m sorry, that definition %s found.' % (code.bold('wasn\'t')))
    response = response.split('</div><div class="example">', 1)
    do = response[0]
    do = re.sub(r'\<.*?\>', '', do)
    do = h.unescape(do)
    try: response = response[1]
    except: return code.say(do)
    response = response.split('<div class="definition">', 1)
    response = response[1]
    response = response.split('</div><div class="example">', 1)
    dt = response[0]
    dt = re.sub(r'\<.*?\>', '', dt)
    dt = h.unescape(dt)
    try: response = response[1]
    except:
        if (len(do) + len(dt)) > 500:
            return code.say(do)
        else: return code.say(do + code.bold(code.color('blue', ' | ')) + dt)
    response = response.split('<div class="definition">', 1)
    response = response[1]
    response = response.split('</div><div class="example">', 1)
    dth = response[0]
    dth = re.sub(r'\<.*?\>', '', dth)
    dth = h.unescape(dth)
    if (len(do) + len(dt) + len(dth)) > 500:
        return code.say(do + code.bold(code.color('blue', ' | ')) + dt)
    else: return code.say(do + code.bold(code.color('blue', ' | ')) + dt + code.bold(code.color('blue', ' | ')) + dth)
urban.commands = ['urban', 'ur', 'urbandictionary']
urban.example = '.urban pineapples'


if __name__ == '__main__':
    print __doc__.strip()
