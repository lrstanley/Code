#!/usr/bin/env python
'''
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
admin.py - Code Admin Module
http://code.liamstanley.net/
'''

import os

defaultnick = None
def listmods(code, input):
    '''Send a list of the loaded modules ot the user.'''
    if not input.admin: return
    modules = list(set(input.modules))
    code.say('Modules: ' + ', '.join(sorted(modules)) + '.')
listmods.commands = ['modules']
listmods.priority = 'high'
listmods.rate = 20

def join(code, input):
    '''Join the specified channel. This is an admin-only command.'''
    # Can only be done in privmsg by an admin
    if input.sender.startswith('#'): return
    if input.admin:
        channel, key = input.group(1), input.group(2)
        if not key:
            code.write(['JOIN'], channel)
        else: code.write(['JOIN', channel, key])
join.rule = r'(?i)\.join (#\S+)(?: *(\S+))?'
join.priority = 'low'
join.example = '.join #example or .join #example key'

def part(code, input):
    '''Part the specified channel. This is an admin-only command.'''
    # Can only be done in privmsg by an admin
    if input.sender.startswith('#'): return
    if input.admin:
        code.write(['PART'], input.group(2))
part.commands = ['part', 'leave']
part.priority = 'low'
part.example = '.part #example'

def quit(code, input):
    '''Quit from the server. This is an owner-only command.'''
    # Can only be done in privmsg by the owner
    if input.sender.startswith('#'): return
    if input.owner:
        code.write(['QUIT'], 'Terminating Bot.')
        __import__('os')._exit(0)
quit.commands = ['quit', 'terminate', 'shutdown', 'stop']
quit.priority = 'low'

def nick(code, input):
    '''Change nickname dynamically. This is an owner-only command.'''
    global defaultnick
    if not defaultnick:
        defaultnick = code.nick
    if input.owner:
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
    else:
        return
nick.commands = ['name', 'nick', 'nickname']
nick.priority = 'low'

def msg(code, input):
    '''Send a message to a channel, or a user. Admin-only.'''
    # Can only be done in privmsg by an admin
    if input.sender.startswith('#'): return
    a, b = input.group(2), input.group(3)
    if (not a) or (not b): return
    if not input.owner:
        al = a.lower()
        if al == 'chanserv' or al == 'nickserv' or al == 'hostserv' or al == 'memoserv' or al == 'saslserv' or al == 'operserv':
           return
    helper = False
    if hasattr(code.config, 'helpers'):
        if a in code.config.helpers and (input.host in code.config.helpers[a] or (input.nick).lower() in code.config.helpers[a]):
            helper = True
    if input.admin or helper:
        code.msg(a, b)
msg.rule = (['msg', 'say'], r'(?i)(#?\S+) (.+)')
msg.priority = 'low'

def me(code, input):
    '''Send a raw action to a channel/user. Admin-only.'''
    # Can only be done in privmsg by an admin
    if input.sender.startswith('#'): return
    a, b = input.group(2), input.group(3)
    helper = False
    if a in code.config.helpers and (input.host in code.config.helpers[a] or (input.nick).lower() in code.config.helpers[a]):
        helper = True
    if input.admin or helper:
        if a and b:
            msg = '\x01ACTION %s\x01' % input.group(3)
            code.msg(input.group(2), msg, x=True)
me.rule = (['me', 'action'], r'(?i)(#?\S+) (.+)')
me.priority = 'low'

def announce(code, input):
    '''Send an announcement to all channels the bot is in'''
    if not input.admin:
        code.reply('Sorry, I can\'t let you do that')
        return
    print code.channels
    for channel in code.channels:
        code.msg(channel, code.color('purple', code.bold('[ANNOUNCMENT] ')) + input.group(2))
announce.commands = ['announce', 'broadcast']
announce.example = '.announce Some important message here'

def blocks(code, input):
    '''Command to add/delete user records, for a filter system. This is to prevent users from abusing Code.'''
    if not input.admin:
        return code.reply(code.color('red','You are not authorized to use this feature!'))

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
        syntax = 'Syntax: \'.blocks list <nick|hostmask>\''
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
        syntax = 'Syntax: \'.blocks add <nick|hostmask> <args>\''
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
        syntax = 'Syntax: \'.blocks del <nick|hostmask> <args>\''
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
        code.reply('Syntax: \'.blocks <add|del|list> <nick|hostmask> [args]\'')

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
blocks.priority = 'low'
blocks.thread = False

char_replace = {
        r'\x01': chr(1),
        r'\x02': chr(2),
        r'\x03': chr(3),
        }

def write_raw(code, input):
    '''Send a raw command ot the server. WARNING THIS IS DANGEROUS! Owner-only.'''
    if not input.owner: return
    txt = input.bytes[7:]
    txt = txt.encode('utf-8')
    a = txt.split(':')
    status = False
    if len(a) > 1:
        newstr = a[1]
        for x in char_replace:
            if x in newstr:
                newstr = newstr.replace(x, char_replace[x])
        code.write(a[0].split(), newstr, raw=True)
        status = True
    elif a:
        b = a[0].split()
        code.write([b[0].strip()], u' '.join(b[1:]), raw=True)
        status = True
    if status:
        code.reply('Message sent to server.')
write_raw.commands = ['write', 'raw']
write_raw.priority = 'high'
write_raw.thread = False

if __name__ == '__main__':
    print __doc__.strip()