#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
ask.py - Code Ask Module
http://code.liamstanley.io/
"""

import random, time
import re
from util.hook import *

def ask(code, input):
    """ask <item1> or <item2> or <item3> - Randomly picks from a set of items seperated by ' or '."""
    if empty(code, input): return
    choices = input.group(2)
    random.seed()

    if choices == None:
        code.reply("Please try a valid question.")
    elif choices.lower() == "what is the answer to life, the universe, and everything?":
        code.reply("42")
    else:
        list_choices = choices.split(" or ")
        if len(list_choices) == 1:
            code.reply(random.choice(['yes', 'no']))
        else:
            choices = choices.replace('?','')
            choices = choices.replace('!','')
            code.reply((random.choice(list_choices)).encode('utf-8'))
ask.commands = ['ask']
ask.priority = 'low'
ask.example = 'ask today or tomorrow or next week'

def rand(code, input):
    """rand <arg1> <arg2> - Generates a random integer between <arg1> and <arg2>."""
    if empty(code, input): return
    syntax = 'Syntax: \'%srand <number> <number>\'' % code.prefix
    toolong = 'Woah man! That\'s really long!'
    msg = input.group(2)
    
    try:
        if ',' in msg:
            # Assume the user is doing .rand #,#
            first,second = msg.strip().split(',',1)
            first = int(first)
            second = int(second)
            if too_long(first) or too_long(second):
                return code.reply(toolong)
            if first > second:
                small = second
                big = first
            else:
                small = first
                big = second

        elif ' ' in msg and len(msg.split()) == 2:
            # Assume the user is doing .rand # #
            first,second = msg.strip().split()
            first = int(first)
            second = int(second)
            if too_long(first) or too_long(second):
                return code.reply(toolong)
            if first > second:
                small = second
                big = first
            else:
                small = first
                big = second
        else:
            return code.reply(syntax)

        # Now respond
        number = str(random.randint(small,big))
        return code.reply('Your random integer is: {red}%s' % number)
    except:
        return code.reply(syntax)
rand.commands = ['rand']
rand.example = 'rand 100 500'

def too_long(integer):
    if len(str(integer)) > 10:
        return True
    else:
        return False

if __name__ == '__main__':
    print __doc__.strip()