#!/usr/bin/env python
"""
Stan-Derp Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
tools.py - Stan-Derp Tools
http://standerp.liamstanley.net/
"""

def deprecated(old): 
   def new(standerp, input, old=old): 
      self = standerp
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
