#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
quote.py - Code Quote Module
http://code.liamstanley.io/
"""

import random
import modules.unicode as uc
from util.hook import *


@hook(cmds=['addquote'], priority='low', ex='addquote <liam> HERPDERPTRAINS', rate=30, admin=True, args=True)
def addquote(code, input):
    '''addquote <nick> something they said here -- adds the quote to the quote database.'''
    fn = open('quotes.txt', 'a')
    output = uc.encode(input.group(2))
    fn.write(output)
    fn.write('\n')
    fn.close()
    code.reply('Quote added.')


@hook(cmds=['quote'], priority='low', ex='quote 2', rate=30)
def retrievequote(code, input):
    '''quote <number> -- displays a given quote'''
    text = input.group(2)
    try:
        fn = open('quotes.txt', 'r')
    except:
        return code.reply('Please add a quote first.')

    lines = fn.readlines()
    MAX = len(lines)
    fn.close()
    random.seed()
    try:
        number = int(text)
        if number < 0:
            number = MAX - abs(number) + 1
    except:
        try:
            number = random.randint(1, MAX)
        except:
            return code.reply('{red}I\'m sorry, there currently aren\'t any quote in the database. Use .addquote to add one!')
    if not (0 <= number <= MAX):
        code.reply(code.color('red', 'I\'m not sure which quote you would like to see.'))
    else:
        line = lines[number - 1]
        code.reply('Quote {blue}%s{c} of {blue}%s{c}: ' % (number, MAX) + line)


@hook(cmds=['rmquote', 'delquote'], priority='low', ex='delquote 2', rate=30, admin=True, args=True)
def delquote(code, input):
    '''delquote <number> -- removes a given quote from the database. Can only be done by the owner of the bot.'''
    text = input.group(2)
    number = int()
    try:
        fn = open('quotes.txt', 'r')
    except:
        return code.reply('{red}No quotes to delete.')
    lines = fn.readlines()
    fn.close()
    try:
        number = int(text)
    except:
        code.reply('Please enter the quote number you would like to delete.')
        return
    newlines = lines[:number - 1] + lines[number:]
    fn = open('quotes.txt', 'w')
    for line in newlines:
        txt = uc.encode(line)
        if txt:
            fn.write(txt)
            if txt[-1] != '\n':
                fn.write('\n')
    fn.close()
    code.reply('{green}Successfully deleted quote {b}%s{b}.' % (number))
