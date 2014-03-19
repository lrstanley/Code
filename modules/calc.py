#!/usr/bin/env python
# coding=utf-8
"""
Code Copyright (C) 2012-2014 Liam Stanley
calc.py - Code Calculator Module
http://code.liamstanley.io/
"""

import re, json
import urllib, urllib2
import web
from tools import *

uri = 'http://api.duckduckgo.com/?q=%s&format=json'

def calc(code, input):
    if empty(code, input): return
    try:
        data = json.loads(urllib2.urlopen(uri % urllib.quote(input.group(2))).read())
        if data['AnswerType'] != 'calc':
            return code.reply('Failed to calculate')
        #print data['Answer']
        answer = re.sub(r'\<.*?\>', '', data['Answer']).strip()
        return code.say(answer)
    except:
        return code.reply('Failed to calculate!')
calc.commands = ['c', 'calc', 'calculate']
calc.example = 'calc 5 + 3'

def py(code, input):
    # Prevention from spam, along with exploits on Atheme/Charybdis networks
    # (see line 41, new fix)
    if empty(code, input): return
    query = input.group(2).encode('utf-8')
    uri = 'http://tumbolia.appspot.com/py/'
    try:
         answer = web.get(uri + web.urllib.quote(query))
         if answer:
              # Strip line endings from the response, to prevent cut-off
              # Of multi-line responses
              answer = answer.replace('\n',' ').replace('\t',' ').replace('\r','')
              # Make sure to reply result, so we don't run into Fantasy-prefix
              # Channel command issues/security holes
              code.reply(answer)
         else:
              code.reply('Sorry, no {b}%s{b}')
    except Exception, e:
         code.reply('{red}The server did not return an answer.')
         print '[.py]', e
py.commands = ['py', 'python']
py.example = 'py print(int(1.0) + int(3))'

def wa(code, input):
    """Wolphram Alpha search"""
    if empty(code, input): return
    query = input.group(2).encode('utf-8')
    uri = 'http://tumbolia.appspot.com/wa/'
    answer = web.get(uri + web.urllib.quote(query.replace('+', '%2B')))
    if answer: 
        code.say(answer)
    else: code.reply('Sorry, no result.')
wa.commands = ['wa']
wa.example = 'wa 1 mile in feet'

if __name__ == '__main__': 
    print __doc__.strip()