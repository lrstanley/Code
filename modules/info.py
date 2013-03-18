#!/usr/bin/env python
"""
Stan-Derp Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
info.py - Stan-Derp Information Module
http://standerp.liamstanley.net/
"""

def doc(standerp, input): 
   """Shows a command's documentation, and possibly an example."""
   name = input.group(1)
   name = name.lower()

   if standerp.doc.has_key(name): 
      standerp.reply(standerp.doc[name][0])
      if standerp.doc[name][1]: 
         standerp.say('e.g. ' + standerp.doc[name][1])
doc.rule = ('$nick', '(?i)(?:help|doc) +([A-Za-z]+)(?:\?+)?$')
doc.example = '$nickname: doc tell?'
doc.priority = 'low'

def commands(standerp, input): 
   # This function only works in private message
   if input.sender.startswith('#'): return
   names = ', '.join(sorted(standerp.doc.iterkeys()))
   standerp.say('Commands I recognise: ' + names + '.')
   standerp.say(("For help, do '%s: help example?' where example is the " + 
               "name of the command you want help for. Stan-Derp Copyright Liam Stanley 2013.") % standerp.nick)
commands.commands = ['commands']
commands.priority = 'low'

def help(standerp, input): 
   response = (
      'Hi, I\'m a bot. Say ".commands" to me in private for a list ' + 
      'of my commands, or see ' + standerp.config.website + ' for more ' + 
      'general details. My owner is %s.'
   ) % standerp.config.owner
   standerp.reply(response)
help.rule = ('$nick', r'(?i)help(?:[?!]+)?$')
help.priority = 'low'

def stats(standerp, input): 
   """Show information on command usage patterns."""
   commands = {}
   users = {}
   channels = {}

   ignore = set(['f_note', 'startup', 'message', 'noteuri'])
   for (name, user), count in standerp.stats.items(): 
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
   standerp.say(creply.rstrip(', '))

   # most heavy users
   reply = 'power users: '
   for count, user in userank[:10]: 
      reply += '%s (%s), ' % (user, count)
   standerp.say(reply.rstrip(', '))

   # most heavy channels
   chreply = 'power channels: '
   for count, channel in charank[:3]: 
      chreply += '%s (%s), ' % (channel, count)
   standerp.say(chreply.rstrip(', '))
stats.commands = ['stats']
stats.priority = 'low'

if __name__ == '__main__': 
   print __doc__.strip()
