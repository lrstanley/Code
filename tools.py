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

def admin(code, input):
    if input.owner: return True
    code.say('{b}{red}You are not authorized to use that command!')

def notauthed(code):
    response = '{b}{red}You are not authorized to use that command!'
    code.say(response)

def owner(code, input):
    if input.owner: return True
    code.say('{b}{red}You are not authorized to use that command!')

# /SOME/ of these ones are decorators customized to respond from call()
#    in bot.py and defaults in bind_commands() (mainly admin/owner)

def hook(commands=None, cmds=None, example=None, ex=None, rate=None, rule=None, priority=None,
         thread=None, args=None, admin=None, owner=None):
    def add_attribute(func):
        if commands != None: func.commands = commands
        if cmds != None: func.commands = cmds
        if example != None: func.example = example
        if rate != None: func.rate = rate
        if rule != None: func.rule = rule
        if priority != None: func.priority = priority
        if thread != None: func.thread = thread
        if args != None: func.args = args
        if admin != None: func.admin = admin
        if owner != None: func.owner = owner
        return func
    return add_attribute


if __name__ == '__main__':
    print __doc__.strip()