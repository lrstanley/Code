import re
from util.hook import *


def check_normal(code, input):
    """Globalized fail checklist"""
    if not input.sender.startswith('#'):
        return {'success': False}
    nick = input.group(2)
    verify = auth_check(code, input.sender, input.nick, nick)
    if not verify:
        notauthed(code)
        return {'success': False}
    if input.group(2):
        nick = input.group(2)
    else:
        nick = input.nick
    return {'success': True, 'nick': nick}


def auth_check(code, channel, nick, target=None):
    """
    Checks if nick is on the auth list and returns true if so
    """
    if target == code.nick:
        return 0
    if code.chan[channel][nick]['op']:
        return 1
    return 0


def configureHostMask(mask):
    if mask == '*!*@*':
        return mask
    if re.match('^[^.@!/]+$', mask) is not None:
        return '%s!*@*' % mask
    if re.match('^[^@!]+$', mask) is not None:
        return '*!*@%s' % mask

    m = re.match('^([^!@]+)@$', mask)
    if m is not None:
        return '*!%s@*' % m.group(1)

    m = re.match('^([^!@]+)@([^@!]+)$', mask)
    if m is not None:
        return '*!%s@%s' % (m.group(1), m.group(2))

    m = re.match('^([^!@]+)!(^[!@]+)@?$', mask)
    if m is not None:
        return '%s!%s@*' % (m.group(1), m.group(2))
    return ''


def op(code, input):
    """op <user> - Op users in a room. If no nick is given, input user is selected."""
    check = check_normal(code, input)
    if not check['success']:
        return
    code.write(['MODE', input.sender, "+o", check['nick']])
op.commands = ['op']
op.priority = 'low'


def deop(code, input):
    """deop <user> - Deop users in a room. If no nick is given, input user is selected."""
    check = check_normal(code, input)
    if not check['success']:
        return
    code.write(['MODE', input.sender, "-o", check['nick']])
deop.commands = ['deop']
deop.priority = 'low'


def voice(code, input):
    """voice <user> - Voice users in a room. If no nick is given, input user is selected."""
    check = check_normal(code, input)
    if not check['success']:
        return
    code.write(['MODE', input.sender, "+v", check['nick']])
voice.commands = ['voice']
voice.priority = 'low'


def devoice(code, input):
    """devoice <user> - Devoice users in a room. If no nick is given, input user is selected."""
    check = check_normal(code, input)
    if not check['success']:
        return
    code.write(['MODE', input.sender, "-v", check['nick']])
devoice.commands = ['devoice']
devoice.priority = 'low'


def kick(code, input):
    if not input.admin:
        return
    text = input.group().split()
    argc = len(text)
    if argc < 2:
        return
    opt = text[1]
    nick = opt
    channel = input.sender
    reasonidx = 2
    if opt.startswith('#'):
        if argc < 3:
            return
        nick = text[2]
        channel = opt
        reasonidx = 3
    reason = ' '.join(text[reasonidx:])
    if nick != code.nick:
        code.write(['KICK', channel, nick, reason])
kick.commands = ['kick']
kick.priority = 'high'


def ban(code, input):
    """
    This give admins the ability to ban a user.
    The bot must be a Channel Operator for this command to work.
    """
    if not input.admin:
        return
    text = input.group().split()
    argc = len(text)
    if argc < 2:
        return
    opt = text[1]
    banmask = opt
    channel = input.sender
    if opt.startswith('#'):
        if argc < 3:
            return
        channel = opt
        banmask = text[2]
    banmask = configureHostMask(banmask)
    if banmask == '':
        return
    code.write(['MODE', channel, '+b', banmask])
ban.commands = ['ban']
ban.priority = 'high'


def unban(code, input):
    """
    This give admins the ability to unban a user.
    The bot must be a Channel Operator for this command to work.
    """
    if not input.admin:
        return
    text = input.group().split()
    argc = len(text)
    if argc < 2:
        return
    opt = text[1]
    banmask = opt
    channel = input.sender
    if opt.startswith('#'):
        if argc < 3:
            return
        channel = opt
        banmask = text[2]
    banmask = configureHostMask(banmask)
    if banmask == '':
        return
    code.write(['MODE', channel, '-b', banmask])
unban.commands = ['unban']
unban.priority = 'high'


def quiet(code, input):
    """
    This gives admins the ability to quiet a user.
    The bot must be a Channel Operator for this command to work
    """
    if not input.admin:
        return
    text = input.group().split()
    argc = len(text)
    if argc < 2:
        return
    opt = text[1]
    quietmask = opt
    channel = input.sender
    if opt.startswith('#'):
        if argc < 3:
            return
        quietmask = text[2]
        channel = opt
    quietmask = configureHostMask(quietmask)
    if quietmask == '':
        return
    code.write(['MODE', channel, '+q', quietmask])
quiet.commands = ['quiet', 'mute']
quiet.priority = 'high'


def unquiet(code, input):
    """
    This gives admins the ability to unquiet a user.
    The bot must be a Channel Operator for this command to work
    """
    if not input.admin:
        return
    text = input.group().split()
    argc = len(text)
    if argc < 2:
        return
    opt = text[1]
    quietmask = opt
    channel = input.sender
    if opt.startswith('#'):
        if argc < 3:
            return
        quietmask = text[2]
        channel = opt
    quietmask = configureHostMask(quietmask)
    if quietmask == '':
        return
    code.write(['MODE', channel, '-q', quietmask])
unquiet.commands = ['unquiet', 'unmute']
unquiet.priority = 'high'


def kickban(code, input):
    """
    This gives admins the ability to kickban a user.
    The bot must be a Channel Operator for this command to work
    .kickban [#chan] user1 user!*@* get out of here
    """
    if not input.admin:
        return
    text = input.group().split()
    argc = len(text)
    if argc < 4:
        return
    opt = text[1]
    nick = opt
    mask = text[2]
    reasonidx = 3
    if opt.startswith('#'):
        if argc < 5:
            eturn
        channel = opt
        nick = text[2]
        mask = text[3]
        reasonidx = 4
    reason = ' '.join(text[reasonidx:])
    mask = configureHostMask(mask)
    if mask == '':
        return
    code.write(['MODE', channel, '+b', mask])
    code.write(['KICK', channel, nick, ' :', reason])
kickban.commands = ['kickban', 'kb']
kickban.priority = 'high'


def topic(code, input):
    """
    This gives admins the ability to change the topic.
    Note: One does *NOT* have to be an OP, one just has to be on the list of
    admins.
    """
    if not input.admin:
        return
    text = input.group().split()
    topic = ' '.join(text[1:])
    if topic == '':
        return
    code.write(['PRIVMSG', 'ChanServ'], 'TOPIC %s %s' % (input.sender, topic))
    return
topic.commands = ['topic']
topic.priority = 'low'
