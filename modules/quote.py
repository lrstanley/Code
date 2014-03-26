#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
quote.py - Code Quote Module
http://code.liamstanley.io/
"""

import random
import modules.unicode as uc
from util.hook import *


def addquote(code, input):
    '''.addquote <nick> something they said here -- adds the quote to the quote database.'''
    if not admin(code, input): return
    if empty(code, input): return
    fn = open('quotes.txt', 'a')
    output = uc.encode(input.group(2))
    fn.write(output)
    fn.write('\n')
    fn.close()
    code.reply('Quote added.')
addquote.commands = ['addquote']
addquote.priority = 'low'
addquote.example = 'addquote <liam> HERPDERPTRAINS'
addquote.rate = 30


def retrievequote(code, input):
    '''.quote <number> -- displays a given quote'''
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
        try: number = random.randint(1, MAX)
        except: return code.reply('{red}I\'m sorry, there currently aren\'t any quote in the database. Use .addquote to add one!')
    if not (0 <= number <= MAX):
        code.reply(code.color('red','I\'m not sure which quote you would like to see.'))
    else:
        line = lines[number - 1]
        code.reply('Quote {blue}%s{c} of {blue}%s{c}: ' % (number, MAX) + line)
retrievequote.commands = ['quote']
retrievequote.priority = 'low'
retrievequote.example = 'quote 2'
retrievequote.rate = 30


def delquote(code, input):
    '''.rmquote <number> -- removes a given quote from the database. Can only be done by the owner of the bot.'''
    if not admin(code, input): return
    if empty(code, input): return
    text = input.group(2)
    number = int()
    try:
        fn = open('quotes.txt', 'r')
    except:
        return code.reply('{red}No quotes to delete.')
    lines = fn.readlines()
    MAX = len(lines)
    fn.close()
    try:
        number = int(text)
    except:
        code.reply('Please enter the quote number you would like to delete.')
        return
    newlines = lines[:number-1] + lines[number:]
    fn = open('quotes.txt', 'w')
    for line in newlines:
        txt = uc.encode(line)
        if txt:
            fn.write(txt)
            if txt[-1] != '\n':
                fn.write('\n')
    fn.close()
    code.reply('{green}Successfully deleted quote {b}%s{b}.' % (number))
delquote.commands = ['rmquote', 'delquote','deletequote','removequote']
delquote.priority = 'low'
delquote.example = 'rmquote 2'
delquote.rate = 30


if __name__ == '__main__':
    print __doc__.strip()