#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
lmgtfy.py - Code 'Let Me Google That For You' Module
http://code.liamstanley.io/
"""

import re
from util.hook import *
from util.web import shorten


@hook(cmds=['lmgtfy'], ex='lmgtfy linux', args=True)
def lmgtfy(code, input):
    """Let my Google That For You"""
    lmgtfy = input.group(2)
    lmgtfy = re.sub(r"[^\w\s]", ' ', lmgtfy).replace(".", " ").replace(" ", "+")
    while lmgtfy.find('++') > -1:
        lmgtfy = lmgtfy.replace("++", "+").strip("+")
    while lmgtfy.find(' ') > -1:
        lmgtfy = lmgtfy.replace(" ", "").strip(" ")
    lmgtfyurl = "http://lmgtfy.com/?q=" + lmgtfy
    if hasattr(code.config, 'shortenurls'):
        if code.config.shortenurls:
            lmgtfyurl = shorten(lmgtfyurl)
    code.say(input.nick + ": " + lmgtfyurl)