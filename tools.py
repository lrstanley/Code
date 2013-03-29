#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
tools.py - Code Tools
http://code.liamstanley.net/
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

if __name__ == '__main__':
    print __doc__.strip()
