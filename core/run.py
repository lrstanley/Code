#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
run.py - Code Initialization Module
https://www.liamstanley.io/Code.git
"""

import sys
import os
import time
import threading
import signal
from core import bot
from util import output


class Watcher(object):
    def __init__(self):
        self.child = os.fork()
        if self.child != 0:
            self.watch()

    def watch(self):
        try:
            os.wait()
        except KeyboardInterrupt:
            output.error('Terminating the bot...')
            self.kill()
        sys.exit()

    def kill(self):
        try:
            os.kill(self.child, signal.SIGKILL)
        except OSError:
            pass


def run_code(config):
    if hasattr(config, 'delay'):
        delay = config.delay
    else:
        delay = 20

    def connect(config):
        p = bot.Code(config)
        p.run(config.host, config.port)

    try:
        Watcher()
    except Exception, e:
        output.error('%s (in core/__init__.py)' % e)

    while True:
        try:
            connect(config)
        except KeyboardInterrupt:
            sys.exit()

        if not isinstance(delay, int):
            break

        output.error('Disconnected. Reconnecting in %s seconds...' % delay)
        time.sleep(delay)


def run(config):
    t = threading.Thread(target=run_code, args=(config,))
    t.run()
