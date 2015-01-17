#!/usr/bin/env python2
"""
Code Copyright (C) 2012-2015 Liam Stanley
Source: https://github.com/Liamraystanley/Code
Docs: https://www.liamstanley.io/Code.git
"""

import sys
sys.dont_write_bytecode = True
import os
import re
import json
import optparse
import time
import traceback
from multiprocessing import Process
from core import bot
from util import output

dotdir = os.path.expanduser('~/.code')
configv = 7
threads = []


def docstring():
    symbol = '*'
    lines = __doc__.strip().split('\n')
    largest = 0
    for line in lines:
        if len(line) > largest:
            largest = len(line)
    outer = (largest + (1 * 4)) * symbol
    output.normal(outer, False)
    for line in lines:
        tmp = symbol + (1 * ' ') + line
        sidedif = (largest + (1 * 4)) - len(tmp) - 1
        tmp += ' ' * sidedif + symbol
        output.normal(tmp, False)
    output.normal(outer, False)
    output.normal('Initializing the bot', 'START')


def parse_json(filename):
    """ remove //-- and /* -- */ style comments from JSON """
    comment_re = re.compile(
        '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
        re.DOTALL | re.MULTILINE
    )
    with open(filename) as f:
        content = f.read()
        match = comment_re.search(content)
        while match:
            content = content[:match.start()] + content[match.end():]
            match = comment_re.search(content)

        return json.loads(content)


def setupServer(server):
    defaults = {
        'website': 'https://www.liamstanley.io/Code.git',
        'name': '\x0307Code -- Python IRC Bot',
        'user': 'code',
        'port': 6667,
        'server_password': None
    }

    for key, value in defaults.iteritems():
        if key not in server:
            server[key] = value
            continue
        if not server[key]:
            server[key] = value

    if server['host'] == 'irc.example.net':
        error = 'You must edit the config file first!'
        output.error(error)
        sys.exit(1)
    return server


def main(argv=None):
    # 1: Parse The Command Line

    parser = optparse.OptionParser('%prog [options]')
    parser.add_option(
        '-c', '--config', metavar='fn',
        help='use this configuration file or directory'
    )
    opts, args = parser.parse_args(argv)

    # 2: Documentation output
    docstring()

    # 3: Require python 2.7 or later
    if sys.version_info < (2, 7):
        output.error('Requires Python 2.7 or later, from www.python.org')
        sys.exit(1)

    # 4. Create ~/.code if not made already
    if not os.path.isdir(dotdir):
        if not os.path.isdir(dotdir):
            try:
                output.info(
                    'Creating database directory in ~/.code...')
                os.mkdir(dotdir)
            except Exception as e:
                output.error('There was a problem creating %s:' % dotdir)
                output.error(str(e))
                output.error('Please fix this and then run code again.')
                sys.exit(1)

    # 5: Load The Configuration
    bot_config = opts.config or 'config.json'

    # and check if exists
    if not os.path.isfile(bot_config):
        output.error(
            'Configuration file "%s" does not exist. Please copy '
            'the example.json to config.json then run Code again' % bot_config)
        sys.exit(1)

    try:
        config = parse_json(bot_config)
    except Exception as e:
        output.error(
            'The config file has syntax errors. Please fix them and run Code again!'
            '\n' + str(e)
        )
        sys.exit(1)

    global threads
    if 'servers' not in config:
        # Backwards compatible with old config.json files
        config = {'servers': [config]}
    for server in config['servers']:
        if server['host'] == 'irc.anotherexample.net':
            continue
        id = len(threads)
        process = Process(target=connect, args=(id, setupServer(server),))
        process.daemon = True
        process.start()
        threads.append({'id': id, 'config': server, 'process': process})
        time.sleep(5)


def connect(id, config):
    while True:
        try:
            # Todo, pass thread number, if more than one thread, pass in
            # console
            bot.Code(config).run(id, config['host'], config['port'])
        except:
            output.error('Error in process (Server: %s, port: %s)' % (config['host'], config['port']))
            output.error(traceback.format_exc())
            delay = config['connect_delay'] if 'connect_delay' in config else 20
            output.error('Terminating and restarting in {} seconds...'.format(delay))
            time.sleep(int(delay))
            output.error('Restarting...')
            pass


if __name__ == '__main__':
    try:
        main()
        while True:
            time.sleep(1)
            if len(threads) == 0:
                output.error(
                    'No more processes to manage. Exiting...', 'ERROR')
                sys.exit()
            for id in range(len(threads)):
                p = threads[id]['process']
                if p.exitcode == 0:
                    # Assume it exited safely. Ignore the termination.
                    p.terminate()
                    output.success('Terminating process ID %s (%s:%s)' % (
                        id, threads[id]['config']['host'], threads[id]['config']['port']), 'STATUS')
                    del threads[id]
                    break
                if p.exitcode == 1:
                    # Exited erronously. We'll just assume it wants a reboot.
                    p.terminate()
                    p = Process(
                        target=connect, args=(id, setupServer(threads[id]['config']),))
                    p.daemon = True
                    output.success('Regenerating process ID %s (%s:%s)' % (
                        id, threads[id]['config']['host'], threads[id]['config']['port']), 'STATUS')
                    p.start()
                    threads[id]['process'] = p
    except KeyboardInterrupt:
        output.success('Shutting down bot...', 'REQUEST')
        sys.exit()
