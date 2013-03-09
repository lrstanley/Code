#!/usr/bin/env python
"""
Stan-Derp Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
startup.py - Stan-Derp Startup Module
http://standerp.liamstanley.net/
"""

import threading, time

def setup(standerp): 
   # by clsn
   standerp.data = {}
   refresh_delay = 300.0

   if hasattr(standerp.config, 'refresh_delay'):
      try: refresh_delay = float(standerp.config.refresh_delay)
      except: pass

      def close():
         print "Nobody PONGed our PING, restarting"
         standerp.handle_close()
      
      def pingloop():
         timer = threading.Timer(refresh_delay, close, ())
         standerp.data['startup.setup.timer'] = timer
         standerp.data['startup.setup.timer'].start()
         # print "PING!"
         standerp.write(('PING', standerp.config.host))
      standerp.data['startup.setup.pingloop'] = pingloop

      def pong(standerp, input):
         try:
            # print "PONG!"
            standerp.data['startup.setup.timer'].cancel()
            time.sleep(refresh_delay + 60.0)
            pingloop()
         except: pass
      pong.event = 'PONG'
      pong.thread = True
      pong.rule = r'.*'
      standerp.variables['pong'] = pong

      # Need to wrap handle_connect to start the loop.
      inner_handle_connect = standerp.handle_connect

      def outer_handle_connect():
         inner_handle_connect()
         if standerp.data.get('startup.setup.pingloop'):
            standerp.data['startup.setup.pingloop']()

      standerp.handle_connect = outer_handle_connect

def startup(standerp, input): 
   import time

   if hasattr(standerp.config, 'serverpass'): 
      standerp.write(('PASS', standerp.config.serverpass))

   if hasattr(standerp.config, 'password'): 
      standerp.msg('NickServ', 'IDENTIFY %s' % standerp.config.password)
      time.sleep(5)

   # Cf. http://swhack.com/logs/2005-12-05#T19-32-36
   for channel in standerp.channels: 
      standerp.write(('JOIN', channel))
      time.sleep(0.5)
startup.rule = r'(.*)'
startup.event = '251'
startup.priority = 'low'

if __name__ == '__main__': 
   print __doc__.strip()
