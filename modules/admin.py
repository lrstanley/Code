#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
admin.py - Code Admin Module
http://code.liamstanley.net/
"""

import os

def join(code, input):
    """Join the specified channel. This is an admin-only command."""
    # Can only be done in privmsg by an admin
    if input.sender.startswith('#'): return
    if input.admin:
        channel, key = input.group(1), input.group(2)
        if not key:
            code.write(['JOIN'], channel)
        else: code.write(['JOIN', channel, key])
join.rule = r'\.join (#\S+)(?: *(\S+))?'
join.priority = 'low'
join.example = '.join #example or .join #example key'

def part(code, input):
    """Part the specified channel. This is an admin-only command."""
    # Can only be done in privmsg by an admin
    if input.sender.startswith('#'): return
    if input.admin:
        code.write(['PART'], input.group(2))
part.commands = ['part', 'leave']
part.priority = 'low'
part.example = '.part #example'

def quit(code, input):
    """Quit from the server. This is an owner-only command."""
    # Can only be done in privmsg by the owner
    if input.sender.startswith('#'): return
    if input.owner:
        code.write(['QUIT'], 'Terminating Bot.')
        __import__('os')._exit(0)
quit.commands = ['quit', 'terminate', 'shutdown', 'stop']
quit.priority = 'low'

def nick(code, input):
    """Change nickname dynamically. This is an owner-only command."""
    #if input.sender.startswith('#'): return
    if input.owner:
        try:
            if code.changenick(input.group(2)):
                code.changenick(input.group(2)) #have to do command twice, solution?
                pass
            else:
                code.say('Failed to change username!')
        except:
            code.say('Failed to change username!')
    else:
        return
nick.commands = ['name', 'nick', 'nickname']
nick.priority = 'low'

def msg(code, input):
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
msg.rule = (['msg', 'say'], r'(#?\S+) (.+)')
msg.priority = 'low'

def me(code, input):
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
me.rule = (['me', 'action'], r'(#?\S+) (.*)')
me.priority = 'low'

def announce(code, input):
    """Send an announcement to all channels the bot is in"""
    if not input.admin:
        code.reply('Sorry, I can\'t let you do that')
        return
    print code.channels
    for channel in code.channels:
        code.msg(channel, code.color('purple', code.bold('[ANNOUNCMENT] ')) + input.group(2))
announce.commands = ['announce', 'broadcast']
announce.example = '.announce Some important message here'

def defend_ground(code, input):
    """
    This function monitors all kicks across all channels code is in. If he
    detects that he is the one kicked he'll automatically join that channel.

    WARNING: This may not be needed and could cause problems if code becomes
    annoying. Please use this with caution.
    """
    channel = input.sender
    code.write(['JOIN'], channel)
defend_ground.event = 'KICK'
defend_ground.rule = '.*'
defend_ground.priority = 'low'

def blocks(code, input):
    if not input.admin: return

    STRINGS = {
            "success_del" : "Successfully deleted block: %s",
            "success_add" : "Successfully added block: %s",
            "no_nick" : "No matching nick block found for: %s",
            "no_host" : "No matching hostmask block found for: %s",
            "invalid" : "Invalid format for %s a block. Try: .blocks add (nick|hostmask) code",
            "invalid_display" : "Invalid input for displaying blocks.",
            "nonelisted" : "No %s listed in the blocklist.",
            'huh' : "I could not figure out what you wanted to do.",
            }

    if not os.path.isfile("blocks"):
        blocks = open("blocks", "w")
        blocks.write('\n')
        blocks.close()

    blocks = open("blocks", "r")
    contents = blocks.readlines()
    blocks.close()

    try: masks = contents[0].replace("\n", "").split(',')
    except: masks = ['']

    try: nicks = contents[1].replace("\n", "").split(',')
    except: nicks = ['']

    text = input.group().split()

    if len(text) == 3 and text[1] == "list":
        if text[2] == "hostmask":
            if len(masks) > 0 and masks.count("") == 0:
                for each in masks:
                    if len(each) > 0:
                        code.say("blocked hostmask: " + each)
            else:
                code.reply(STRINGS['nonelisted'] % ('hostmasks'))
        elif text[2] == "nick":
            if len(nicks) > 0 and nicks.count("") == 0:
                for each in nicks:
                    if len(each) > 0:
                        code.say("blocked nick: " + each)
            else:
                code.reply(STRINGS['nonelisted'] % ('nicks'))
        else:
            code.reply(STRINGS['invalid_display'])

    elif len(text) == 4 and text[1] == "add":
        if text[2] == "nick":
            nicks.append(text[3])
        elif text[2] == "hostmask":
            masks.append(text[3].lower())
        else:
            code.reply(STRINGS['invalid'] % ("adding"))
            return

        code.reply(STRINGS['success_add'] % (text[3]))

    elif len(text) == 4 and text[1] == "del":
        if text[2] == "nick":
            try:
                nicks.remove(text[3])
                code.reply(STRINGS['success_del'] % (text[3]))
            except:
                code.reply(STRINGS['no_nick'] % (text[3]))
                return
        elif text[2] == "hostmask":
            try:
                masks.remove(text[3].lower())
                code.reply(STRINGS['success_del'] % (text[3]))
            except:
                code.reply(STRINGS['no_host'] % (text[3]))
                return
        else:
            code.reply(STRINGS['invalid'] % ("deleting"))
            return
    else:
        code.reply(STRINGS['huh'])

    os.remove("blocks")
    blocks = open("blocks", "w")
    masks_str = ",".join(masks)
    if len(masks_str) > 0 and "," == masks_str[0]:
        masks_str = masks_str[1:]
    blocks.write(masks_str)
    blocks.write("\n")
    nicks_str = ",".join(nicks)
    if len(nicks_str) > 0 and "," == nicks_str[0]:
        nicks_str = nicks_str[1:]
    blocks.write(nicks_str)
    blocks.close()

blocks.commands = ['blocks']
blocks.priority = 'low'
blocks.thread = False

char_replace = {
        r"\x01": chr(1),
        r"\x02": chr(2),
        r"\x03": chr(3),
        }

def write_raw(code, input):
    if not input.owner: return
    txt = input.bytes[7:]
    txt = txt.encode('utf-8')
    a = txt.split(":")
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
        code.write([b[0].strip()], u" ".join(b[1:]), raw=True)
        status = True
    if status:
        code.reply("Message sent to server.")
write_raw.commands = ['write', 'raw']
write_raw.priority = 'high'
write_raw.thread = False

if __name__ == '__main__':
    print __doc__.strip()

