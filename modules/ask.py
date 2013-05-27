#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
ask.py - Code Ask Module
http://code.liamstanley.net/
"""

import random, time


def ask(code, input):
    """.ask <item1> or <item2> or <item3> - Randomly picks from a set of items seperated by ' or '."""

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
            choices.rstrip("?")
            code.reply((random.choice(list_choices)).encode('utf-8'))
ask.commands = ['ask']
ask.priority = 'low'
ask.example = '.ask today or tomorrow or next week'

if __name__ == '__main__':
    print __doc__.strip()
