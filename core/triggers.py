#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
triggers.py - Code IRC Raw Trigger Module
https://www.liamstanley.io/Code.git
"""

from util import output
import time
import os


def trigger_001(code, origin, line, args, text):
    if not code.debug:
        output.normal('({}) {}'.format(origin.nick, origin.text), 'NOTICE')


def trigger_002(code, origin, line, args, text):
    if not code.debug:
        output.normal('({}) {}'.format(origin.nick, origin.text), 'NOTICE')


def trigger_003(code, origin, line, args, text):
    output.normal('({}) {}'.format(origin.nick, origin.text), 'NOTICE')


def trigger_005(code, origin, line, args, text):
    tmp = args[2:-1]
    for item in tmp:
        if not '=' in item:
            code.server_options[item] = True
        else:
            name, data = item.split('=', 1)
            code.server_options[name] = data


def trigger_250(code, origin, line, args, text):
    if not code.debug:
        output.normal('({}) {}'.format(origin.nick, origin.text), 'NOTICE')


def trigger_251(code, origin, line, args, text):
    return trigger_250(code, origin, line, args, text)


def trigger_255(code, origin, line, args, text):
    return trigger_250(code, origin, line, args, text)


def trigger_352(code, origin, line, args, text):
    return trigger_354(code, origin, line, args, text, is_352=True)


def trigger_353(code, origin, line, args, text):
    # NAMES event
    channel, user_list = args[3], args[4]
    channel, user_list = '#' + \
        channel.split('#', 1)[1].strip(), user_list.strip().split()
    if channel not in code.chan:
        code.chan[channel] = {}
    if channel not in code.logs['channel']:
        code.logs['channel'][channel] = []
    for user in user_list:
        # Support servers with %, &, and ~, as well as standard @, and +
        if user.startswith('@') or user.startswith('%') or user.startswith('&') or user.startswith('~'):
            name, normal, voiced, op = user[1::], True, False, True
        elif user.startswith('+'):
            name, normal, voiced, op = user[1::], True, True, False
        else:
            name, normal, voiced, op = user, True, False, False
        code.chan[channel][name] = {'normal': normal, 'voiced':
                                    voiced, 'op': op, 'count': 0, 'messages': []}


def trigger_354(code, origin, line, args, text, is_352=False):
    if not is_352:
        if len(args) != 7:
            return  # Probably error
        if args[2] != '1':  # We sent it on channel join, get it
            return
        channel, ident, host, nick = args[3], args[4], args[5], args[6]
    else:
        channel, ident, host, nick = args[2], args[3], args[4], args[6]
    code.chan[channel][nick]['ident'] = ident
    code.chan[channel][nick]['host'] = host
    code.chan[channel][nick]['first_seen'] = int(time.time())
    code.chan[channel][nick]['last_seen'] = int(time.time())


def trigger_433(code, origin, line, args, text):
    if not code.debug:
        output.warning('Nickname {} is already in use. Trying another..'.format(code.nick))
    nick = code.nick + '_'
    code.write(('NICK', nick))
    code.nick = nick.encode('ascii', 'ignore')


def trigger_437(code, origin, line, args, text):
    if not code.debug:
        output.error(text)
    os._exit(1)


def trigger_NICK(code, origin, line, args, text):
    if not code.debug:
        output.normal('{} is now known as {}'.format(origin.nick, args[1]), 'NICK')

    # Rename old users to new ones in the database...
    for channel in code.chan:
        if origin.nick in code.chan[channel]:
            old = code.chan[channel][origin.nick]
            del code.chan[channel][origin.nick]
            code.chan[channel][args[1]] = old
            code.chan[channel][args[1]]['last_seen'] = int(time.time())

    tmp = {
        'message': 'is now known as {}'.format(args[1]),
        'nick': origin.nick,
        'time': int(time.time()),
        'channel': 'NICK'
    }
    code.logs['bot'].append(tmp)


def trigger_PRIVMSG(code, origin, line, args, text):
    text = code.stripcolors(text)
    if text.startswith('\x01ACTION'):
        text = '(me) ' + text.split(' ', 1)[1].strip('\x01')
    if not code.debug:
        output.normal('({}) {}'.format(origin.nick, text), args[1])

    # Stuff for user_list
    if args[1].startswith('#'):
        if origin.nick not in code.chan[args[1]]:
            code.chan[args[1]][origin.nick] = {'normal': True, 'voiced':
                                               False, 'op': False, 'count': 0, 'messages': []}
        code.chan[args[1]][origin.nick]['count'] += 1
        # 1. per-channel-per-user message storing...
        code.chan[args[1]][origin.nick]['messages'].append(
            {'time': int(time.time()), 'message': text})
        # Ensure it's not more than 20 of the last messages
        code.chan[args[1]][origin.nick]['messages'] = code.chan[
            args[1]][origin.nick]['messages'][-20:]
        # 2. Per channel message storing...
        tmp = {'message': text, 'nick': origin.nick,
               'time': int(time.time()), 'channel': args[1]}
        code.logs['channel'][args[1]].append(tmp)
        code.logs['channel'][args[1]] = code.logs['channel'][args[1]][-20:]
        # 3. All bot messages in/out, maxed out by n * 100 (n being number of
        # channels)
        code.logs['bot'].append(tmp)
        code.logs['bot'] = code.logs['bot'][-(100 * len(code.channels)):]

    for channel in code.chan:
        if origin.nick in code.chan[channel]:
            code.chan[channel][origin.nick]['last_seen'] = int(time.time())


def trigger_NOTICE(code, origin, line, args, text):
    if 'Invalid password for ' in text:
        if not code.debug:
            output.error('Invalid NickServ password')
        os._exit(1)
    if 'AUTHENTICATION SUCCESSFUL as ' in args[2]:
        if code.config('undernet_hostmask'):
            code.write(('MODE', code.nick, '+x'))
    if not code.debug:
        output.normal('({}) {}'.format(origin.nick, text), 'NOTICE')
    # Add notices to the bot logs
    tmp = {
        'message': text,
        'nick': origin.nick,
        'time': int(time.time()),
        'channel': 'NOTICE'
    }
    code.logs['bot'].append(tmp)


def trigger_KICK(code, origin, line, args, text):
    output.normal('{} has kicked {} from {}. Reason: {}'.format(
        origin.nick, args[2], args[1], args[3]), 'KICK', 'red')
    del code.chan[args[1]][args[2]]


def trigger_MODE(code, origin, line, args, text):
    if len(args) == 3:
        if not code.debug:
            output.normal('{} sets MODE {}'.format(origin.nick, text), 'MODE')
        return
    else:
        if not code.debug:
            output.normal('{} sets MODE {}'.format(origin.nick, args[2]), args[1])

    # Stuff for user_list
    data = ' '.join(args[1:])

    channel, modes, users = data.strip().split(' ', 2)
    users = users.split()
    tmp = []

    def remove(old, sign):
        tmp = []
        modes = []
        for char in old:
            modes.append(char)
        while sign in modes:
            i = modes.index(sign)
            tmp.append(i)
            del modes[i]
        return tmp, ''.join(modes)

    if modes.startswith('+'):
        _plus, new_modes = remove(modes, '+')
        _minus, new_modes = remove(new_modes, '-')
    else:
        _minus, new_modes = remove(modes, '-')
        _plus, new_modes = remove(new_modes, '+')

    for index in range(len(users)):
        _usr = users[index]
        _mode = new_modes[index]
        _sign = ''
        if index in _plus:
            _sign = '+'
        if index in _minus:
            _sign = '-'
        tmp.append({'name': _usr, 'mode': _mode, 'sign': _sign})

    last_used = ''

    for index in range(len(tmp)):
        if not last_used:
            last_used = tmp[index]['sign']
        if not tmp[index]['sign'] or len(tmp[index]['sign']) == 0:
            tmp[index]['sign'] = last_used
        else:
            last_used = tmp[index]['sign']

    names = {'v': 'voiced', 'o': 'op', '+': True, '-': False}
    for user in tmp:
        if user['mode'] in names and user['sign'] in names:
            mode, name, sign = names[user['mode']
                                     ], user['name'], names[user['sign']]
            code.chan[channel][name][mode] = sign
            if mode == 'op' and sign:
                code.chan[channel][name]['voiced'] = True


def trigger_JOIN(code, origin, line, args, text):
    if origin.nick != code.nick:
        code.chan[args[1]][origin.nick] = {'normal': True, 'voiced':
                                           False, 'op': False, 'count': 0, 'messages': []}
    if not code.debug:
        output.normal('{} has joined {}'.format(origin.nick, args[1]), args[1])
    tmp = {
        'message': 'joined {}'.format(args[1]),
        'nick': origin.nick,
        'time': int(time.time()),
        'channel': 'JOIN'
    }
    code.logs['bot'].append(tmp)
    code.write(('WHO', origin.nick, '%tcuhn,1'))


def trigger_PART(code, origin, line, args, text):
    if origin.nick == code.nick:
        del code.chan[args[1]]
        del code.logs['channel'][args[1]]
    else:
        del code.chan[args[1]][origin.nick]
    if len(args) == 3:
        reason = args[2]
    else:
        reason = 'Unknown'
    if not code.debug:
        output.normal('{} has part {}. Reason: {}'.format(origin.nick, args[1], reason), args[1])
    tmp = {
        'message': 'left {}'.format(args[1]),
        'nick': origin.nick,
        'time': int(time.time()),
        'channel': 'PART'
    }
    code.logs['bot'].append(tmp)


def trigger_write_PART(code, args, text, raw):
    del code.chan[args[1]]
    del code.logs['channel'][args[1]]


def trigger_QUIT(code, origin, line, args, text):
    for channel in code.chan:
        if origin.nick in channel:
            del code.chan[channel][origin.nick]
    tmp = {
        'message': '',
        'nick': origin.nick,
        'time': int(time.time()),
        'channel': 'QUIT'
    }
    code.logs['bot'].append(tmp)
