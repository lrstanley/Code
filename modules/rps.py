#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
rps.py - Code Rock Paper Scissors Module
http://code.liamstanley.io/
"""

import random
from util.hook import *

@hook(cmds=['rock','paper','scissors'], rate=15)
def rps(code, input):
    """Play some Rock-Paper-Scissors with Code!"""
    text = input.group().lower()
    text = text.split()
    cpu = random.randint(1,3)
    if cpu == 1:
        state = 'had a draw'
        color = 'blue'
    elif cpu == 2:
        state = 'won'
        color = 'green'
    else:
        state = 'lost'
        color = 'red'
               # 1=tie, 2=win, 3=loss
    syntax = 'The syntax is .(rock/paper/scissors)'
    if input.group(1) == 'rock':
        if cpu == 1:
            response = 'rock'
        elif cpu == 2:
            response = 'scissors'
        else:
            response = 'paper'
    elif input.group(1) == 'paper':
        if cpu == 1:
            response = 'paper'
        elif cpu == 2:
            response = 'rock'
        else:
            response = 'scissors'
    elif input.group(1) == 'scissors':
        if cpu == 1:
            response = 'scissors'
        elif cpu == 2:
            response = 'paper'
        else:
            response = 'rock'
    return code.say('*Rock... Paper... Scissors!* You {%s}{b}%s{b}! %s had {b}%s{b}!' % (color,
                    state, code.nick, response))