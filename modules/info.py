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
   if input.sender.startswith('#'):
       code.say(('%s: Please %s me that command.') % (input.nick, code.bold('query')))
   else:
#depricated method, inaccurate
#   names = ', '.join(sorted(code.doc.iterkeys()))
#   code.say('Commands I recognise: ' + names + '.')
      code.say(('The list of commands for %s is extensive, so they are now ' +
                  'located here: https://github.com/Liamraystanley/Code/wiki#features') % code.bold(code.nick))
      code.say(('For help, do \'%s: %s\' where example is the ' + 
                  'name of the command you want help for.') % (code.nick, code.color('green', 'help example?')))
commands.commands = ['commands', 'command', 'cmd', 'cmds']
commands.priority = 'low'

def help(code, input):
   try:
      website = code.config.website
   except: #revert to default - The Code homepage.
      website = 'http://code.liamstanley.net'
   response = (
      'Hi, I\'m a bot. Say \'%s\' to me in private for a list ' + 
      'of my commands, or see ' + website + ' for more general details.' + 
      ' %s is my owner.'
   ) % (code.color('purple', '.commands'), code.color('gold', code.config.owner))
   code.reply(response)
#old regex method
#help.rule = ('$nick', r'(?i)help(?:[?!]+)?$')
help.commands = ['help', 'support']
help.priority = 'low'
help.rate = 30

def about(code, input):
   response = (
      code.nick + ' was developed by Liam Stanley and many others. ' + code.nick + ' is a open-source ' + 
      'Python Modular IRC Bot, that serves as a fun, fast, and collective resource ' + 
      'for large, and small channels. More info: http://code.liamstanley.net'
   )
   code.reply(response)
about.commands = ['about', 'liam']
about.priority = 'low'
about.rate = 60


def issue(code, input):
   code.reply('Having an issue with ' + code.bold(code.nick) + '? Post a bug report here:')
   code.say('https://github.com/Liamraystanley/Code/issues/new')
issue.commands = ['report', 'issue', 'makeissue', 'bug', 'bugreport', 'makebug', 'issues', 'createissue']
issue.priority = 'low'
issue.rate = 60

def stats(code, input): 
   """Show information on command usage patterns."""
   commands = {}
   users = {}
   channels = {}

   ignore = set(['f_note', 'startup', 'message', 'noteuri',
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
   creply = code.color('green', 'most used commands: ')
   for count, command in comrank[:10]: 
      creply += '%s (%s), ' % (command, count)
   code.say(creply.rstrip(', '))

   # most heavy users
   reply = code.color('blue', 'power users: ')
   for count, user in userank[:10]: 
      reply += '%s (%s), ' % (user, count)
   code.say(reply.rstrip(', '))

   # most heavy channels
   chreply = code.color('purple', 'power channels: ')
   for count, channel in charank[:3]: 
      chreply += '%s (%s), ' % (channel, count)
   code.say(chreply.rstrip(', '))
stats.commands = ['stats']
stats.priority = 'low'

if __name__ == '__main__': 
   print __doc__.strip()
