#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
startup.py - Code Startup Module
http://code.liamstanley.io/
"""

import threading, time

def setup(code):
    # by clsn
    code.data = {}
    refresh_delay = 300.0

    if hasattr(code.config, 'refresh_delay'):
        try: refresh_delay = float(code.config.refresh_delay)
        except: pass

        def close():
            print "Nobody PONGed our PING, restarting"
            code.handle_close()

        def pingloop():
            timer = threading.Timer(refresh_delay, close, ())
            code.data['startup.setup.timer'] = timer
            code.data['startup.setup.timer'].start()
            # print "PING!"
            code.write(('PING', code.config.host))
        code.data['startup.setup.pingloop'] = pingloop

        def pong(code, input):
            try:
                # print "PONG!"
                code.data['startup.setup.timer'].cancel()
                time.sleep(refresh_delay + 60.0)
                pingloop()
            except: pass
        pong.event = 'PONG'
        pong.thread = True
        pong.rule = r'.*'
        code.variables['pong'] = pong

        # Need to wrap handle_connect to start the loop.
        inner_handle_connect = code.handle_connect

        def outer_handle_connect():
            inner_handle_connect()
            if code.data.get('startup.setup.pingloop'):
                code.data['startup.setup.pingloop']()

        code.handle_connect = outer_handle_connect

def startup(code, input):
    import time

    if hasattr(code.config, 'password'):
        code.msg('NickServ', 'IDENTIFY %s' % code.config.password)
        time.sleep(5)

    # Cf. http://swhack.com/logs/2005-12-05#T19-32-36
    for channel in code.channels:
        code.join(channel)
        time.sleep(0.5)
startup.rule = r'.*'
startup.event = '251'
startup.priority = 'low'

if __name__ == '__main__':
    print __doc__.strip()
