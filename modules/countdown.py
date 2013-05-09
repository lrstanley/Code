#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
countdown.py - Code countdown Module
http://code.liamstanley.net/
"""

import datetime

def generic_countdown(code, input):
    """ .countdown <year> <month> <day> - displays a countdown to a given date. """
    try:
        text = input.group(2).split()
    except:
        code.say(code.color('red', 'Please use correct format: .countdown <year> <month> <day>'))
    if text[0].isdigit() and text[1].isdigit() and text[2].isdigit() and len(text) == 3:
        diff = datetime.datetime(int(text[0]), int(text[1]), int(text[2])) - datetime.datetime.today()
        code.say(str(diff.days) + "-days " +  str(diff.seconds/60/60) + "-hours " +  str(diff.seconds/60 - diff.seconds/60/60 * 60) + "-minutes until " + text[0] + " " + text[1] + " " + text[2])
    else:
        code.say(code.color('red', 'Please use correct format: .countdown <year> <month> <day>'))
generic_countdown.commands = ['countdown']
generic_countdown.priority = 'low'


if __name__ == '__main__':
    print __doc__.strip()
