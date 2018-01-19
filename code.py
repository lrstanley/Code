#!/usr/bin/env python2
"""
Code Copyright (C) 2012-2015 Liam Stanley
Source/docs: https://github.com/lrstanley/Code
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
from util.tools import hash

dotdir = os.path.expanduser('~/.code')
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
    output.success('Initializing the bot', 'START')


def parse_json(filename):
    """ remove //-- and /* -- */ style comments from JSON """
    comment_re = re.compile('(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?', re.DOTALL | re.MULTILINE)
    with open(filename) as f:
        content = f.read()
        match = comment_re.search(content)
        while match:
            content = content[:match.start()] + content[match.end():]
            match = comment_re.search(content)

        contents = json.loads(content)

    if 'servers' not in content:
        # Backwards compatible with old config.json files
        contents = {'servers': [contents]}

    return contents


def setupServer(server):
    defaults = {
        'website': 'https://github.com/lrstanley/Code',
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
        output.error('Requires Python 2.7.x, from www.python.org')
        sys.exit(1)

    # 4. Create ~/.code if not made already
    if not os.path.isdir(dotdir):
        try:
            output.info('Creating database directory in ~/.code...')
            os.mkdir(dotdir)
        except Exception as e:
            output.error('There was a problem creating %s:' % dotdir)
            output.error(e)
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
        output.error('The config file has syntax errors. Please fix them and run Code again!\n' + str(e))
        sys.exit(1)

    global threads

    for server in config['servers']:
        if server['host'] == 'irc.anotherexample.net':
            continue
        id = len(threads)
        process = Process(target=connect, args=(id, setupServer(server),))
        process.daemon = True
        process.start()
        threads.append({'id': id, 'config': server, 'process': process})
        time.sleep(5)

    # 6: Begin managing these processes
    try:
        # set some temporary variables that we will be using for config
        # file version checking
        conf_last_check = int(time.time())
        conf_last_mtime = int(os.path.getmtime(bot_config))
        while True:
            time.sleep(1)
            if (int(time.time()) - conf_last_check) > 10 and int(os.path.getmtime(bot_config)) > conf_last_mtime:
                conf_last_check = int(time.time())
                conf_last_mtime = int(os.path.getmtime(bot_config))
                try:
                    # If the new configuration file isn't the same as the last
                    # one that we saved, attempt to re-import it
                    config_new = parse_json(bot_config)
                    if len(config_new['servers']) == len(config['servers']) and len(config_new['servers']) == len(threads):
                        output.success('Configuration file %s has changed! Use the restart command to take affect!' % bot_config)
                        config = config_new
                        for i in range(len(config['servers'])):
                            # Once they reboot that connection, it should autoload
                            # the new config.
                            threads[i]['config'] = config['servers'][i]
                except Exception as e:
                    # Only spit out errors once per file modification
                    output.error("Configuration file has been changed, however I cannot read it! (%s)" % str(e))
            if len(threads) == 0:
                output.warning('No more processes to manage. Exiting...')
                sys.exit(1)
            for id in range(len(threads)):
                p = threads[id]['process']
                if p.exitcode == 0:
                    # Assume it exited safely. Ignore the termination.
                    p.terminate()
                    output.status('Terminating process ID #%s (%s:%s)' % (id, threads[id]['config']['host'], threads[id]['config']['port']))
                    del threads[id]
                    break
                if p.exitcode == 1:
                    # Exited erronously. We'll just assume it wants a reboot.
                    p.terminate()
                    p = Process(target=connect, args=(id, setupServer(threads[id]['config']),))
                    p.daemon = True
                    delay = threads[id]['config']['connect_delay'] if 'connect_delay' in threads[id]['config'] else 20
                    output.error('Restarting process id #%s (%s:%s) in %s seconds.' % (
                        id, threads[id]['config']['host'], threads[id]['config']['port'], str(delay)
                    ))
                    time.sleep(delay)
                    output.status('Regenerating process ID #%s (%s:%s)' % (id, threads[id]['config']['host'], threads[id]['config']['port']))
                    p.start()
                    threads[id]['process'] = p
    except KeyboardInterrupt:
        output.success('Shutting down bot...', 'REQUEST')
        for id in range(len(threads)):
            p = threads[id]['process']
            output.status('Terminating process ID #%s (%s:%s)' % (id, threads[id]['config']['host'], threads[id]['config']['port']))
            p.terminate()
        time.sleep(1)
        sys.exit(0)


def connect(id, config):
    bot.Code(config).run(id, config['host'], config['port'])


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(0)
    except:
        output.error(traceback.format_exc())
