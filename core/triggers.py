#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
run.py - Code Initialization Module
https://www.liamstanley.io/Code.git
"""

from util import output
import re
import time
import os


def trigger_250(code, line):
    msg, sender = line.split(':', 2)[2], line.split(':', 2)[1].split()[0]
    output.normal('(%s) %s' % (sender, msg), 'NOTICE')


def trigger_251(code, line):
    return trigger_250(code, line)


def trigger_255(code, line):
    return trigger_250(code, line)


def trigger_353(code, line):
    # NAMES event
    channel, user_list = line[1::].split(':', 1)
    channel, user_list = '#' + \
        channel.split('#', 1)[1].strip(), user_list.strip().split()
    if channel not in code.chan:
        code.chan[channel] = {}
    for user in user_list:
        # Support servers with %, &, and ~, as well as standard @, and +
        if user.startswith('@') or user.startswith('%') or user.startswith('&') or user.startswith('~'):
            name, normal, voiced, op = user[1::], True, True, True
        elif user.startswith('+'):
            name, normal, voiced, op = user[1::], True, True, False
        else:
            name, normal, voiced, op = user, True, False, False
        code.chan[channel][name] = {'normal': normal, 'voiced':
                                    voiced, 'op': op, 'count': 0, 'messages': []}


def trigger_433(code, line):
    output.warning('Nickname %s is already in use. Trying another..' %
                   code.nick)
    nick = code.nick + '_'
    code.write(('NICK', nick))
    code.nick = nick.encode('ascii', 'ignore')


def trigger_437(code, line):
    output.error(line.split(':', 2)[2])
    os._exit(1)


def trigger_NICK(code, line):
    nick = line[1::].split('!', 1)[0]
    new_nick = line[1::].split(':', 1)[1]
    output.normal('%s is now known as %s' % (nick, new_nick), 'NICK')


def trigger_PRIVMSG(code, line):
    re_tmp = r'^\:(.*?)\!(.*?)\@(.*?) PRIVMSG (.*?) \:(.*?)$'
    nick, ident, host, sender, msg = re.compile(re_tmp).match(line).groups()
    msg = code.stripcolors(msg)
    if msg.startswith('\x01'):
        msg = '(me) ' + msg.split(' ', 1)[1].strip('\x01')
    output.normal('(%s) %s' % (nick, msg), sender)

    # Stuff for user_list
    if sender.startswith('#'):
        if nick not in code.chan[sender]:
            code.chan[sender][nick] = {'normal': True, 'voiced':
                                       False, 'op': False, 'count': 0, 'messages': []}
        code.chan[sender][nick]['count'] += 1
        code.chan[sender][nick]['messages'].append(
            {'time': int(time.time()), 'message': msg})
        # Ensure it's not more than 20 of the last messages
        code.chan[sender][nick]['messages'] = code.chan[
            sender][nick]['messages'][-20:]


def trigger_NOTICE(code, line):
    re_tmp = r'^\:(.*?) NOTICE (.*?) \:(.*?)$'
    nick, sender, msg = re.compile(re_tmp).match(line).groups()
    if 'Invalid password for ' in msg:
        output.error('Invalid NickServ password')
        os._exit(1)
    output.normal('(%s) %s' % (nick.split('!')[0], msg), 'NOTICE')


def trigger_KICK(code, line):
    re_tmp = r'^\:(.*?)\!(.*?)\@(.*?) KICK (.*?) (.*?) \:(.*?)$'
    nick, ident, host, sender, kicked, reason = re.compile(
        re_tmp).match(line).groups()
    output.normal('%s has kicked %s from %s. Reason: %s' %
                  (nick, kicked, sender, reason), 'KICK', 'red')

    # Stuff for user_list
    tmp = line.split('#', 1)[1].split()
    channel, name = '#' + tmp[0], tmp[1]
    del code.chan[channel][name]


def trigger_MODE(code, line):
    re_tmp = r'^\:(.*?)\!(.*?)\@(.*?) MODE (.*?)$'
    try:
        nick, ident, host, args = re.compile(re_tmp).match(line).groups()
    except:
        return
    output.normal('%s sets MODE %s' % (nick, args), 'MODE')

    # Stuff for user_list
    data = line.split('MODE', 1)[1]
    if len(data.split()) >= 3:
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


def trigger_JOIN(code, line):
    name = line[1::].split('!', 1)[0]
    channel = line.split('JOIN', 1)[1].strip()
    if name != code.nick:
        code.chan[channel][name] = {'normal': True, 'voiced':
                                    False, 'op': False, 'count': 0, 'messages': []}


def trigger_PART(code, line):
    name = line[1::].split('!', 1)[0]
    channel = line.split('PART', 1)[1].split()[0]
    del code.chan[channel][name]


def trigger_QUIT(code, line):
    name = line[1::].split('!', 1)[0]
    for channel in code.chan:
        if name in channel:
            del code.chan[channel][name]
