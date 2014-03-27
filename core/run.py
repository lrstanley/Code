#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
__init__.py - Code Init Module
http://code.liamstanley.io/
"""

import sys, os, time, threading, signal
#import bot
from core import bot

class Watcher(object):
    def __init__(self):
        self.child = os.fork()
        if self.child != 0:
            self.watch()

    def watch(self):
        try: os.wait()
        except KeyboardInterrupt:
            self.kill()
        sys.exit()

    def kill(self):
        try: os.kill(self.child, signal.SIGKILL)
        except OSError: pass

def run_code(config):
    if hasattr(config, 'delay'):
        delay = config.delay
    else: delay = 20

    def connect(config):
        p = bot.Code(config)
        p.run(config.host, config.port)

    try: Watcher()
    except Exception, e:
        print >> sys.stderr, 'Warning:', e, '(in __init__.py)'

    while True:
        try: connect(config)
        except KeyboardInterrupt:
            sys.exit()

        if not isinstance(delay, int):
            break

        warning = 'Warning: Disconnected. Reconnecting in %s seconds...' % delay
        print >> sys.stderr, warning
        time.sleep(delay)

def run(config):
    t = threading.Thread(target=run_code, args=(config,))
    if hasattr(t, 'run'):
        t.run()
    else: t.start()

if __name__ == '__main__':
    print __doc__