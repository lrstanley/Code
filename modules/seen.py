#!/usr/bin/env python
"""
Stan-Derp Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
seen.py - Stan-Derp Seen Module
http://standerp.liamstanley.net/
"""

import time
from tools import deprecated

def seen(standerp, input): 
   """.seen <nick> - Reports when <nick> was last seen."""
   nick = input.group(2)
   if not nick:
      return standerp.reply("Need a nickname to search for...")
   nick = nick.lower()

   if not hasattr(standerp, 'seen'): 
      return standerp.reply("?")

   if standerp.seen.has_key(nick): 
      channel, t = standerp.seen[nick]
      t = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(t))

      msg = "I last saw %s at %s on %s" % (nick, t, channel)
      standerp.reply(msg)
   else: standerp.reply("Sorry, I haven't seen %s around." % nick)
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
