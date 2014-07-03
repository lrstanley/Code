import os
import sys
from util.hook import *

defaultnick = None


@hook(cmds=['modules'], rate=20, priority='high', admin=True)
def listmods(code, input):
    '''Send a list of the loaded modules to the user.'''
    return code.say('Modules: %s.' % ', '.join(code.modules))


@hook(cmds=['join'], ex='join #example key', admin=True, args=True)
def join(code, input):
    '''Join the specified channel. This is an admin-only command.'''
    if len(input.group(2).split()) > 1:  # Channel + key
        return code.write(['JOIN', input.group(2).split(' ', 1)])
    else:
        return code.write(['JOIN'], input.group(2).strip())


@hook(cmds=['part', 'leave'], ex='part #example', admin=True, args=True)
def part(code, input):
    '''Part the specified channel. This is an admin-only command.'''
    return code.write(['PART', input.group(2).strip()])


@hook(cmds=['restart', 'reboot', 'reconnect'], admin=True)
def restart(code, input):
    '''Reconnect to the server. (Fully restarts the server process) This is an admin-only command.'''
    code.restart()


@hook(cmds=['quit', 'disconnect', 'shutdown', 'stop'], owner=True)
def quit(code, input):
    '''Quit from the server. This is an owner-only command.'''
    code.quit()


@hook(cmds=['name', 'nick', 'nickname'], priority='low', owner=True, args=True)
def nick(code, input):
    '''Change nickname dynamically. This is an owner-only command.'''
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
            os._exit(1)


@hook(cmds=['msg', 'say'], ex='msg #L I LOVE PENGUINS.', priority='low', admin=True, args=True)
def msg(code, input):
    '''msg <channel|username> <msg> - Send a message to a channel, or a user. Admin-only.'''
    if len(input.group(2).split()) < 2:
        return code.say('{red}{b}Incorrect usage!: %smsg <channel|username> <msg>' % code.prefix)
    a, b = input.group(2).split(' ', 1)
    if not input.owner and a.lower() in ['chanserv', 'nickserv', 'hostserv', 'memoserv', 'saslserv', 'operserv']:
        return code.say('{red}{b}You\'re not authorized to message those services!')
    code.msg(a, b)


@hook(cmds=['me', 'action'], ex='me #L loves Liam', priority='low', admin=True, args=True)
def me(code, input):
    '''me <channel|username> <msg> - Send a raw ACTION to a channel/user. Admin-only.'''
    msg = input.group(2)
    if len(msg.split()) < 2:
        return code.say('{red}{b}Incorrect usage!: %saction <channel|username> <msg>' % code.prefix)
    msg = msg.split(' ', 1)
    code.me(msg[0], msg[1])

@hook(cmds=['notice'], ex='notice #L Thie bot is awesome!', priority='low', admin=True, args=True)
def notice(code, input):
    '''notice <channel|username> <msg> - Send a raw NOTICE to a channel/user. Admin-only.'''
    msg = input.group(2)
    if len(msg.split()) < 2:
        return code.say('{red}{b}Incorrect usage!: %snotice <channel|username> <msg>' % code.prefix)
    msg = msg.split(' ', 1)
    code.notice(msg[0], msg[1])


@hook(cmds=['announce', 'broadcast'], ex='announce Some important message here', priority='low', admin=True, args=True)
def announce(code, input):
    '''Send an announcement to all channels the bot is in'''
    for channel in code.channels:
        code.msg(channel, '{b}{purple}[ANNOUNCMENT] %s' % input.group(2))


@hook(cmds=['blocks'], ex='blocks add nick MyNameIsSpammer', thread=False, admin=True, args=True)
def blocks(code, input):
    '''Command to add/delete user records, for a filter system. This is to prevent users from abusing Code.'''
    if not os.path.isfile('blocks'):
        blocks = open('blocks', 'w')
        blocks.write('\n')
        blocks.close()

    blocks = open('blocks', 'r')
    contents = blocks.readlines()
    blocks.close()

    try:
        masks = contents[0].replace('\n', '').split(',')
    except:
        masks = ['']

    try:
        nicks = contents[1].replace('\n', '').split(',')
    except:
        nicks = ['']

    text = input.group().strip().split()
    low = input.group().lower().strip().split()

    show = ['list', 'show', 'users', 'blocks']
    host = ['host', 'hostmask', 'hostname']
    name = ['nick', 'name', 'user']
    add = ['add', 'create', 'block']
    delete = ['del', 'delete', 'rem', 'remove', 'unblock']
    # List 'em
    if len(text) >= 2 and low[1] in show:
        syntax = 'Syntax: \'%sblocks list <nick|hostmask>\'' % code.prefix
        if len(text) != 3:
            return code.reply(syntax)
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
        if len(text) != 4:
            return code.reply(syntax)
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
        if len(text) != 4:
            return code.reply(syntax)
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
                code.reply('No matching hostmask block found for: %s' %
                           (text[3]))
                return
        else:
            return code.reply(syntax)
    else:
        code.reply(
            'Syntax: \'%sblocks <add|del|list> <nick|hostmask> [args]\'' % code.prefix)

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

char_replace = {
    r'\x01': chr(1),
    r'\x02': chr(2),
    r'\x03': chr(3),
}


@hook(cmds=['write', 'raw'], priority='high', thread=False, owner=True, args=True)
def write_raw(code, input):
    '''Send a raw command to the server. WARNING THIS IS DANGEROUS! Owner-only.'''
    secure = '{red}That seems like an insecure message. Nope!'
    r = input.group(2).encode('ascii', 'ignore')
    bad = ['ns', 'nickserv', 'chanserv', 'cs',
           'q', 'authserv', 'botserv', 'operserv']
    for bot in bad:
        if (' %s ' % bot) in r.lower():
            return code.reply(secure)
    try:
        args, text = r.split(':')
        args, text = args.strip().split(), text.strip()
    except:
        return code.write(input.group(2), raw=True)
    return code.write(args, text, raw=True)
