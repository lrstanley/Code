#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
ping.py - Code Ping Module
About: http://code.liamstanley.net/
"""

import random

def hello(code, input): 
   greeting = random.choice(('Hi', 'Hey', 'Hello', 'sup', 'Ohai', 'Erro', 'Ello', 'Ohaider'))
   punctuation = random.choice(('', '!'))
   code.say(greeting + ' ' + input.nick + punctuation)
hello.rule = r'(?i)(hi|hello|hey|sup|ello|erro|ohai) $nickname[ \t]*$'

def thanks(code, input): 
   welcome = random.choice(('Your welcome', 'welcome', 'np', 'no prob', 'no problemo'))
   punctuation = random.choice(('', '!'))
   code.say(welcome + ' ' + input.nick + punctuation)
thanks.rule = r'(?i)(thanks|thx|tnx}thank|thnx) $nickname[ \t]*$'

def interjection(code, input): 
   code.say(input.nick + '!')
interjection.rule = r'$nickname!'
interjection.priority = 'high'
interjection.thread = False

if __name__ == '__main__': 
   print __doc__.strip()
