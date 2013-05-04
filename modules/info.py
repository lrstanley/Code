#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
info.py - Code Information Module
http://code.liamstanley.net/
"""

def doc(code, input): 
   """Shows a command's documentation, and possibly an example."""
   name = input.group(1)
   name = name.lower()

   if code.doc.has_key(name): 
      code.reply(code.doc[name][0])
      if code.doc[name][1]: 
         code.say('e.g. ' + code.doc[name][1])
doc.rule = ('$nick', '(?i)(?:help|doc) +([A-Za-z]+)(?:\?+)?$')
doc.example = '$nickname: doc tell?'
doc.priority = 'low'

def commands(code, input): 
   # This function only works in private message
   if input.sender.startswith('#'): return
#depricated method, inaccurate
#   names = ', '.join(sorted(code.doc.iterkeys()))
#   code.say('Commands I recognise: ' + names + '.')
   code.say(("The list of commands for %s is extensive, so they are now located here: https://github.com/Liamraystanley/Code/wiki#features") % code.nick)
   code.say(("For help, do '%s: help example?' where example is the " + 
               "name of the command you want help for. Code Copyright Liam Stanley 2013.") % code.nick)
commands.commands = ['commands', 'cmd', 'cmds']
commands.priority = 'low'

def help(code, input): 
   response = (
      'Hi, I\'m a bot. Say ".commands" to me in private for a list ' + 
      'of my commands, or see ' + code.config.website + ' for more ' + 
      'general details. My owner is %s.'
   ) % code.config.owner
   code.reply(response)
#old regex method
#help.rule = ('$nick', r'(?i)help(?:[?!]+)?$')
help.commands = ['help', 'support']
help.priority = 'low'

def stats(code, input): 
   """Show information on command usage patterns."""
   commands = {}
   users = {}
   channels = {}

   ignore = set(['f_note', 'startup', 'message', 'noteuri',
                 'say_it', 'collectlines', 'oh_baby', 'chat'])
                 'say_it', 'collectlines', 'oh_baby', 'chat',
                 'collect_links'])
   for (name, user), count in code.stats.items(): 
      if name in ignore: continue
      if not user: continue

      if not user.startswith('#'): 
         try: users[user] += count
         except KeyError: users[user] = count
      else: 
         try: commands[name] += count
         except KeyError: commands[name] = count

         try: channels[user] += count
         except KeyError: channels[user] = count

   comrank = sorted([(b, a) for (a, b) in commands.iteritems()], reverse=True)
   userank = sorted([(b, a) for (a, b) in users.iteritems()], reverse=True)
   charank = sorted([(b, a) for (a, b) in channels.iteritems()], reverse=True)

   # most heavily used commands
   creply = 'most used commands: '
   for count, command in comrank[:10]: 
      creply += '%s (%s), ' % (command, count)
   code.say(creply.rstrip(', '))

   # most heavy users
   reply = 'power users: '
   for count, user in userank[:10]: 
      reply += '%s (%s), ' % (user, count)
   code.say(reply.rstrip(', '))

   # most heavy channels
   chreply = 'power channels: '
   for count, channel in charank[:3]: 
      chreply += '%s (%s), ' % (channel, count)
   code.say(chreply.rstrip(', '))
stats.commands = ['stats']
stats.priority = 'low'

if __name__ == '__main__': 
   print __doc__.strip()
