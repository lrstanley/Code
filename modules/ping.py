#!/usr/bin/env python
"""
Stan-Derp Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
ping.py - Stan-Derp Ping Module
About: http://standerp.liamstanley.net/
"""

import random

def hello(standerp, input): 
   greeting = random.choice(('Hi', 'Hey', 'Hello', 'sup', 'Ohai', 'Erro', 'Ello', 'Ohaider'))
   punctuation = random.choice(('', '!'))
   standerp.say(greeting + ' ' + input.nick + punctuation)
hello.rule = r'(?i)(hi|hello|hey|sup|ello|erro|ohai) $nickname[ \t]*$'

def thanks(standerp, input): 
   welcome = random.choice(('Your welcome', 'welcome', 'np', 'no prob', 'no problemo'))
   punctuation = random.choice(('', '!'))
   standerp.say(welcome + ' ' + input.nick + punctuation)
thanks.rule = r'(?i)(thanks|thx|tnx}thank|thnx) $nickname[ \t]*$'

def interjection(standerp, input): 
   standerp.say(input.nick + '!')
interjection.rule = r'$nickname!'
interjection.priority = 'high'
interjection.thread = False

if __name__ == '__main__': 
   print __doc__.strip()
