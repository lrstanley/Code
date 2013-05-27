#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
seen.py - Code Seen Module
http://code.liamstanley.net/
"""

import time
from tools import deprecated

def seen(code, input): 
   """.seen <nick> - Reports when <nick> was last seen."""
   if not match.group(2): return 
   nick = input.group(2)
   if not nick:
      return code.reply('Need a %s to search for...' % code.bold('nickname'))
   nick = nick.lower()
   if not hasattr(code, 'seen'): 
      return code.reply("?")

   if code.seen.has_key(nick): 
      channel, t = code.seen[nick]
      t = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(t))

      msg = "I last saw %s at %s on %s" % (code.color('blue', nick), code.bold(t), code.bold(channel))
      code.reply(msg)
   else: code.reply('Sorry, I haven\'t seen %s around.' % code.color('blue', nick))
seen.rule = (['seen'], r'(\S+)')

@deprecated
def f_note(self, origin, match, args): 
   def note(self, origin, match, args): 
      if not hasattr(self.bot, 'seen'): 
         self.bot.seen = {}
      if origin.sender.startswith('#'): 
         # if origin.sender == '#inamidst': return
         self.seen[origin.nick.lower()] = (origin.sender, time.time())

      # if not hasattr(self, 'chanspeak'): 
      #    self.chanspeak = {}
      # if (len(args) > 2) and args[2].startswith('#'): 
      #    self.chanspeak[args[2]] = args[0]

   try: note(self, origin, match, args)
   except Exception, e: print e
f_note.rule = r'(.*)'
f_note.priority = 'low'

if __name__ == '__main__': 
   print __doc__.strip()
