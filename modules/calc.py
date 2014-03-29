#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
calc.py - Code Calculations Module
http://code.liamstanley.io/
"""

import re, json
import urllib, urllib2
import hashlib
from util.hook import *
from util import web


uri = 'http://api.duckduckgo.com/?q=%s&format=json'


@hook(cmds=['c','calc','calculate'], ex='calc 5 + 3', args=True)
def calc(code, input):
    try:
        data = json.loads(urllib2.urlopen(uri % urllib.quote(input.group(2).replace('^','**'))).read())
        if data['AnswerType'] != 'calc':
            return code.reply('Failed to calculate')
        answer = re.sub(r'\<.*?\>', '', data['Answer']).strip()
        return code.say(answer)
    except:
        return code.reply('Failed to calculate!')


@hook(cmds=['py','python'], ex='py print(int(1.0) + int(3))', args=True)
def py(code, input):
    """python <commands> -- Execute Python inside of a sandbox"""
    query = input.group(2).encode('utf-8')
    uri = 'http://tumbolia.appspot.com/py/'
    try:
        answer = urllib2.urlopen(uri + urllib.quote(query)).read()
        if answer:
            answer = answer.replace('\n',' ').replace('\t',' ').replace('\r','')
            return code.reply(answer)
        else:
            return code.reply('Sorry, no {b}%s{b}')
    except Exception, e:
        return code.reply('{red}The server did not return an answer.')


@hook(cmds=['wa'], ex='wa 1 mile in feet', args=True)
def wa(code, input):
    """Wolphram Alpha search"""
    query = input.group(2)
    uri = 'http://tumbolia.appspot.com/wa/'
    answer = urllib2.urlopen(uri + urllib.quote(query)).read()
    if answer and not 'json stringified precioussss' in answer:
        answer = answer.split(';')
        if len(answer) > 3:
            answer = answer[1]
        answer = '{purple}{b}WolphramAlpha: {c}{b}' + answer
        while '  ' in answer:
            answer = answer.replace('  ', ' ')
        return code.say(web.htmlescape(answer))
    else:
        return code.reply('{red}Sorry, no result.')


@hook(cmds=['md5', 'hash'], priority='low', args=True)
def md5(code, input):
    """md5 <string> -- Create a md5 hash of the input string"""
    return code.say(hashlib.md5(input.group(2)).hexdigest())


@hook(cmds=['sha256'], priority='low', args=True)
def sha256(code, input):
    """sha256 <string> -- Create a sha256 hash of the input string"""
    return code.say(hashlib.sha256(input.group(2)).hexdigest())


@hook(cmds=['sha512'], priority='low', args=True)
def sha512(code, input):
    """sha512 <string> -- Create a sha512 hash of the input string"""
    return code.say(hashlib.sha512(input.group(2)).hexdigest())


if __name__ == '__main__': 
    print __doc__.strip()