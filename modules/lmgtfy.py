#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
lmgtfy.py - Code 'Let Me Google That For You' Server Module
About: http://code.liamstanley.io/
"""

import re

def lmgtfy(code, input): #needs more work for utf-8 encoding. but, meh.
    """Let my Google That For You"""
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
    code.say(input.nick + ": " + lmgtfyurl)
lmgtfy.commands = ['lmgtfy']
lmgtfy.example = '.lmgtfy linux'

if __name__ == '__main__': 
   print __doc__.strip()
