#!/usr/bin/env python
'''
Code Copyright (C) 2012-2014 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
admin.py - Code Admin Module
http://code.liamstanley.io/
'''

import os
from tools import *

defaultnick = None


def listmods(code, input):
    '''Send a list of the loaded modules ot the user.'''
    if not admin(code, input): return
    return code.say('Modules: %s.' % ', '.join(code.modules))
listmods.commands = ['modules']
listmods.priority = 'high'
listmods.rate = 20

def join(code, input):
    '''Join the specified channel. This is an admin-only command.'''
    if not admin(code, input): return
    if empty(code, input): return
    if len(input.group(2).split()) > 1: # Channel + key
        return code.write(['JOIN', input.group(2).split(' ',1)])
    else:
        return code.write(['JOIN'], input.group(2).strip())
join.commands = ['join']
join.example = 'join #example or .join #example key'

def part(code, input):
    '''Part the specified channel. This is an admin-only command.'''
    if not admin(code, input): return
    if empty(code, input): return
    return code.write(['PART', input.group(2).strip()])
part.commands = ['part', 'leave']
part.example = 'part #example'

def quit(code, input):
    '''Quit from the server. This is an owner-only command.'''
    # Can only be done in privmsg by the owner
    if not owner(code, input): return
    if empty(code, input): return
    code.write(['QUIT'], 'Terminating Bot.')
    __import__('os')._exit(0)
quit.commands = ['quit', 'terminate', 'shutdown', 'stop']

def nick(code, input):
    '''Change nickname dynamically. This is an owner-only command.'''
    if not owner(code, input): return
    if empty(code, input): return
    global defaultnick
    if not defaultnick:
        defaultnick = code.nick
    if code.changenick(input.group(2)):
        code.changenick(input.group(2))
        pass
    else:
        code.say('Failed to change username! Trying default!')
        if code.changenick(defaultnick):
            code.changenick(defaultnick)
            pass
        else:
            code.say('Failed to set default, shutting down!')
            __import__('os')._exit(1)
nick.commands = ['name', 'nick', 'nickname']
nick.priority = 'low'

def msg(code, input):
    '''Send a message to a channel, or a user. Admin-only.'''
    if not owner(code, input): return
    if empty(code, input): return
    if input.sender.startswith('#'): return
    a, b = input.group(2), input.group(3)
    if not b: return
    if not input.owner:
        al = a.lower()
        if al == 'chanserv' or al == 'nickserv' or al == 'hostserv' or al == 'memoserv' or al == 'saslserv' or al == 'operserv':
           return
    code.msg(a, b)
msg.rule = (['msg', 'say'], r'(?i)(#?\S+) (.+)')
msg.priority = 'low'
msg.example = 'msg #L I LOVE PENGUINS.'

def me(code, input):
    '''Send a raw action to a channel/user. Admin-only.'''
    if not admin(code, input): return
    if empty(code, input): return
    if input.sender.startswith('#'): return
    a, b = input.group(2), input.group(3)
    if not b: return
    msg = '\x01ACTION %s\x01' % input.group(3)
    code.msg(input.group(2), msg, x=True)
me.rule = (['me', 'action'], r'(?i)(#?\S+) (.+)')
me.priority = 'low'
me.example = 'me #L loves to sing'

def announce(code, input):
    '''Send an announcement to all channels the bot is in'''
    if not admin(code, input): return
    if empty(code, input): return
    print code.channels
    for channel in code.channels:
        code.msg(channel, '{b}{purple}[ANNOUNCMENT] %s' % input.group(2))
announce.commands = ['announce', 'broadcast']
announce.example = 'announce Some important message here'

def blocks(code, input):
    '''Command to add/delete user records, for a filter system. This is to prevent users from abusing Code.'''
    if not admin(code, input): return
    if not os.path.isfile('blocks'):
        blocks = open('blocks', 'w')
        blocks.write('\n')
        blocks.close()

    blocks = open('blocks', 'r')
    contents = blocks.readlines()
    blocks.close()

    try: masks = contents[0].replace('\n', '').split(',')
    except: masks = ['']

    try: nicks = contents[1].replace('\n', '').split(',')
    except: nicks = ['']

    text = input.group().strip().split()
    low = input.group().lower().strip().split()

    show = ['list','show','users','blocks']
    host = ['host','hostmask','hostname']
    name = ['nick','name','user']
    add = ['add','create','block']
    delete = ['del','delete','rem','remove','unblock']
    # List 'em
    if len(text) >= 2 and low[1] in show:
        syntax = 'Syntax: \'%sblocks list <nick|hostmask>\'' % code.prefix
        if len(text) != 3: return code.reply(syntax)
        if low[2] in host:
            if len(masks) > 0 and masks.count('') == 0:
                for nick in masks:
                    blocked = []
                    if len(nick) > 0:
                        blocked.append(nick)
                code.say('Blocked hostmask(s): %s' % ', '.join(blocked))
            else:
                code.reply('No hostmasks have been blocked yet.')
        elif low[2] in name:
            if len(nicks) > 0 and nicks.count('') == 0:
                blocked = []
                for nick in nicks:
                    if len(nick) > 0:
                        blocked.append(nick)
                code.say('Blocked nick(s): %s' % ', '.join(blocked))
            else:
                code.reply('No nicks have been blocked yet.')
        else:
            code.reply(syntax)

    # Wants to add a block
    elif len(text) >= 2 and low[1] in add:
        syntax = 'Syntax: \'%sblocks add <nick|hostmask> <args>\'' % code.prefix
        if len(text) != 4: return code.reply(syntax)
        if low[2] in name:
            nicks.append(text[3])
        elif low[2] in host:
            masks.append(text[3].lower())
        else:
            return code.reply(syntax)

        code.reply('Successfully added block: %s' % (text[3]))

    # Wants to delete a block
    elif len(text) >= 2 and low[1] in delete:
        syntax = 'Syntax: \'%sblocks del <nick|hostmask> <args>\'' % code.prefix
        if len(text) != 4: return code.reply(syntax)
        if low[2] in name:
            try:
                nicks.remove(text[3])
                code.reply('Successfully deleted block: %s' % (text[3]))
            except:
                code.reply('No matching nick block found for: %s' % (text[3]))
                return
        elif low[2] in host:
            try:
                masks.remove(text[3])
                code.reply('Successfully deleted block: %s' % (text[3]))
            except:
                code.reply('No matching hostmask block found for: %s' % (text[3]))
                return
        else:
            return code.reply(syntax)
    else:
        code.reply('Syntax: \'%sblocks <add|del|list> <nick|hostmask> [args]\'' % code.prefix)

    os.remove('blocks')
    blocks = open('blocks', 'w')
    masks_str = ','.join(masks)
    if len(masks_str) > 0 and ',' == masks_str[0]:
        masks_str = masks_str[1:]
    blocks.write(masks_str)
    blocks.write('\n')
    nicks_str = ','.join(nicks)
    if len(nicks_str) > 0 and ',' == nicks_str[0]:
        nicks_str = nicks_str[1:]
    blocks.write(nicks_str)
    blocks.close()

blocks.commands = ['blocks']
blocks.thread = False

char_replace = {
        r'\x01': chr(1),
        r'\x02': chr(2),
        r'\x03': chr(3),
        }

def write_raw(code, input):
    '''Send a raw command to the server. WARNING THIS IS DANGEROUS! Owner-only.'''
    if not owner(code, input): return
    if empty(code, input): return
    secure = '{red}That seems like an insecure message. Nope!'
    r = input.group(2).encode('ascii', 'ignore')
    bad = ['ns', 'nickserv', 'chanserv', 'cs', 'q', 'authserv', 'botserv', 'operserv']
    for bot in bad:
        if (' %s ' % bot) in r.lower():
            return code.reply(secure)
    try:
        args, text = r.split(':')
        args, text = args.strip().split(), text.strip()
    except:
        return code.write(input.group(2), raw=True)
    return code.write(args, text, raw=True)
write_raw.commands = ['write', 'raw']
write_raw.priority = 'high'
write_raw.thread = False

if __name__ == '__main__':
    print __doc__.strip()