#!/usr/bin/env python
# coding=utf-8
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
calc.py - Code Calculator Module
http://code.liamstanley.net/
"""

import re, json
import urllib, urllib2
import web
import unicodedata

r_result = re.compile(r'(?i)<A NAME=results>(.*?)</A>')
r_tag = re.compile(r'<\S+.*?>')

def calc(code, input):
    if not input.group(2): return code.reply('Failed to calculate!')
    try:
        data = json.loads(urllib2.urlopen(uri % urllib.quote(input.group(2))).read())
        if data['AnswerType'] != 'calc':
            return code.reply('Failed to calculate!')
        #print data['Answer']
        answer = re.sub(r'\<.*?\>', '', data['Answer']).strip()
        return code.say(answer)
    except:
        return code.reply('Failed to calculate!')
calc.commands = ['c', 'calc', 'calculate']
calc.example = '.calc 5 + 3'

def py(code, input):
    # Prevention from spam, along with exploits on Atheme/Charybdis networks
    if not input.admin: return
    if not input.group(2):
         return code.reply('Please enter an %s' % code.bold('input'))
    query = input.group(2).encode('utf-8')
    uri = 'http://tumbolia.appspot.com/py/'
    try:
         answer = web.get(uri + web.urllib.quote(query))
         if answer:
              code.say(answer)
         else:
              code.reply('Sorry, no %s' % code.bold('result'))
    except Exception, e:
         code.reply(code.color('red', 'The server did not return an answer.'))
         print '[.py]', e
py.commands = ['py', 'python']
py.example = '.py print(int(1.0) + int(3))'

def wa(code, input): 
    if not input.group(2):
        return code.reply('No search term.')
    query = input.group(2).encode('utf-8')
    uri = 'http://tumbolia.appspot.com/wa/'
    answer = web.get(uri + web.urllib.quote(query.replace('+', '%2B')))
    if answer: 
        code.say(answer)
    else: code.reply('Sorry, no result.')
wa.commands = ['wa']

if __name__ == '__main__': 
    print __doc__.strip()
