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

def hook(commands=None, command=None, cmds=None, cmd=None, example=None, ex=None,
         rate=None, rule=None, priority=None, thread=None, event=None, args=None,
         admin=None, owner=None, voiced=None, op=None):
    def add_attribute(func):
        # This is kinda ugly looking, but it does quite the job.
        if commands != None: func.commands = list(commands)
        if command != None: func.commands = list(command)
        if cmds != None: func.commands = list(cmds)
        if cmd != None: func.commands = list(cmd)
        if example != None: func.example = str(example)
        if ex != None: func.example = str(ex)
        if rate != None: func.rate = int(rate)
        if rule != None: func.rule = str(rule)
        if priority != None: func.priority = str(priority)
        if thread != None: func.thread = bool(thread)
        if event != None: func.event = str(event).upper()
        if args != None: func.args = bool(args)
        if admin != None: func.admin = bool(admin)
        if owner != None: func.owner = bool(owner)
        # Custom to user tracking...
        if voiced != None: func.voiced = bool(voiced)
        if op != None: func.op = bool(op)
        #if op != None:
        #    pass
        return func
    return add_attribute

if __name__ == '__main__':
    print __doc__.strip()