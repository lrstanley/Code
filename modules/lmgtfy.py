#!/usr/bin/env python
"""
Stan-Derp Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
lmgtfy.py - Stan-Derp 'Let Me Google That For You' Server Module
About: http://standerp.liamstanley.net/
"""

import re

def lmgtfy(standerp, input): #needs more work for utf-8 encoding. but, meh.
    """Let my Google That For You"""
    lmgtfy = input.group(2)
    lmgtfy = re.sub(r"[^\w\s]", '', lmgtfy)
    lmgtfy = lmgtfy.replace(".", "")
    lmgtfy = lmgtfy.strip(" ")
    lmgtfy = lmgtfy.replace(" ", "+")
    lmgtfy = lmgtfy.replace("++", "+")
    lmgtfyurl = "http://lmgtfy.com/?q=" + lmgtfy
    # http://stackoverflow.com/questions/1007481/how-do-i-replace-whitespaces-with-underscore-and-vice-versa
    # http://paste.liamstanley.net/index.php?1d
    standerp.say(input.nick + ": " + lmgtfyurl)
lmgtfy.commands = ['lmgtfy']
lmgtfy.example = '.lmgtfy linux'
if __name__ == '__main__': 
   print __doc__.strip()
