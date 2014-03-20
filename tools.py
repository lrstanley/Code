#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
tools.py - Code Tools
http://code.liamstanley.io/
"""


def deprecated(old):
    def new(code, input, old=old):
        self = code
        origin = type('Origin', (object,), {
            'sender': input.sender,
            'nick': input.nick
        })()
        match = input.match
        args = [input.bytes, input.sender, '@@']

        old(self, origin, match, args)
    new.__module__ = old.__module__
    new.__name__ = old.__name__
    return new


def empty(code, input, response=None):
    if not response:
        response = 'No arguments supplied! Try: "{b}{purple}%shelp <command>{b}{r}"' % code.prefix
    if not input.group(2):
        code.say(response)
        return True
    else:
        return False

def error(code):
    code.say('Incorrect usage! Try: "{b}{purple}%shelp <command>{b}{r}"' % code.prefix)

def admin(code, input, response=None):
    if not response:
        response = '{b}{red}You are not authorized to use this command!'
    if not input.admin:
        code.say(response)
        return False
    else:
        return True

def notauthed(code):
    response = '{b}{red}You are not authorized to use this command!'
    code.say(response)

def owner(code, input, response=None):
    if not response:
        response = '{b}{red}You are not authorized to use this command!'
    if not input.owner:
        code.say(response)
        return False
    else:
        return True


# Ignore these. Still under testing.

def adminonly(args):
    def add_attribute(function):
        if args:
            function.admin = True
        return function
    return add_attribute


def hook(*args):
    def add_attribute(function):
        # args is a set() of two indexes. 1st, a list() of cmds, 2nd an example
        if len(args) == 2:
            commands, example = args
        else:
            commands = list(args)[0]
            example = None
        function.commands = commands
        if example:
            function.example = example
        return function
    return add_attribute


def rule(*args):
    def add_attribute(function):
        if len(args) == 2:
            trigger, regex = args
            function.rule = trigger, regex
        else:
            regex = args
            function.rule = regex
        return function
    return add_attribute


def rate(args):
    def add_attribute(function):
        function.rate = int(args)
        return function
    return add_attribute


def all(args):
    def add_attribute(function):
        function.rule = r'.*'
        return function
    return add_attribute


def priority(args):
    def add_attribute(function):
        function.priority = args
        return function
    return add_attribute


def thread(args):
    def add_attribute(function):
        function.thread = args
        return function
    return add_attribute


if __name__ == '__main__':
    print __doc__.strip()