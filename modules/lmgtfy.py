#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
lmgtfy.py - Code 'Let Me Google That For You' Module
http://code.liamstanley.io/
"""

import re
from modules.url import shorten
from tools import *

def lmgtfy(code, input): #needs more work for utf-8 encoding. but, meh.
    """Let my Google That For You"""
    if empty(code, input): return
    lmgtfy = input.group(2)
    lmgtfy = re.sub(r"[^\w\s]", ' ', lmgtfy)
    lmgtfy = lmgtfy.replace(".", " ")
    lmgtfy = lmgtfy.replace(" ", "+")
    while lmgtfy.find('++') > -1:
        lmgtfy = lmgtfy.replace("++", "+")
        lmgtfy = lmgtfy.strip("+")
    while lmgtfy.find(' ') > -1:
        lmgtfy = lmgtfy.replace(" ", "")
        lmgtfy = lmgtfy.strip(" ")
    lmgtfyurl = "http://lmgtfy.com/?q=" + lmgtfy
    code.say(input.nick + ": " + shorten(lmgtfyurl))
lmgtfy.commands = ['lmgtfy']
lmgtfy.example = 'lmgtfy linux'

if __name__ == '__main__': 
   print __doc__.strip()