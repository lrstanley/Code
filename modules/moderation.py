# import re
from random import choice as random
from util.hook import *


def kick_reason():
    return random([
        'Adios!',
        'Goodbye!',
        'To the moon you go!',
        'Kindergarten is elsewhere!',
        '...'
    ])


@hook(cmds=['op'], trusted=True, ischannel=True, selfopped=True)
def op(code, input):
    """ op <user> - Op users in a room. If no nick is given, input user is selected. """
    nick = input.group(2) if input.group(2) else input.nick
    code.write(['MODE', input.sender, "+o", nick])


@hook(cmds=['deop'], trusted=True, ischannel=True, selfopped=True)
def deop(code, input):
    """ deop <user> - Deop users in a room. If no nick is given, input user is selected. """
    nick = input.group(2) if input.group(2) else input.nick
    code.write(['MODE', input.sender, "-o", nick])


@hook(cmds=['voice'], trusted=True, ischannel=True, selfopped=True)
def voice(code, input):
    """ voice <user> - Voice users in a room. If no nick is given, input user is selected. """
    nick = input.group(2) if input.group(2) else input.nick
    code.write(['MODE', input.sender, "+v", nick])


@hook(cmds=['devoice'], trusted=True, ischannel=True, selfopped=True)
def devoice(code, input):
    """ devoice <user> - Devoice users in a room. If no nick is given, input user is selected. """
    nick = input.group(2) if input.group(2) else input.nick
    code.write(['MODE', input.sender, "-v", nick])


@hook(cmds=['kick'], trusted=True, ischannel=True, selfopped=True, ex='kick Liam Abuse!', args=True)
def kick(code, input):
    """ kick <user> [reason] - Kicks a user from the current channel, with a reason if supplied. """
    # .kick <user>
    # .kick <user> <reason>
    text = input.group(2).split()
    if len(text) == 1:
        target = input.group(2)
        reason = False
    else:
        target = text[0]
        reason = ' '.join(text[1::])

    if not reason:
        reason = kick_reason()

    if target != code.nick:
        return code.write(['KICK', input.sender, target], reason)
    else:
        return code.say('...')


# Still need to get stuff done below this line, but it's a start.


# def ban(code, input):
#     """
#     This give admins the ability to ban a user.
#     The bot must be a Channel Operator for this command to work.
#     """
#     if not input.admin:
#         return
#     text = input.group().split()
#     argc = len(text)
#     if argc < 2:
#         return
#     opt = text[1]
#     banmask = opt
#     channel = input.sender
#     if opt.startswith('#'):
#         if argc < 3:
#             return
#         channel = opt
#         banmask = text[2]
#     banmask = configureHostMask(banmask)
#     if banmask == '':
#         return
#     code.write(['MODE', channel, '+b', banmask])
# ban.commands = ['ban']
# ban.priority = 'high'


# def unban(code, input):
#     """
#     This give admins the ability to unban a user.
#     The bot must be a Channel Operator for this command to work.
#     """
#     if not input.admin:
#         return
#     text = input.group().split()
#     argc = len(text)
#     if argc < 2:
#         return
#     opt = text[1]
#     banmask = opt
#     channel = input.sender
#     if opt.startswith('#'):
#         if argc < 3:
#             return
#         channel = opt
#         banmask = text[2]
#     banmask = configureHostMask(banmask)
#     if banmask == '':
#         return
#     code.write(['MODE', channel, '-b', banmask])
# unban.commands = ['unban']
# unban.priority = 'high'


# def quiet(code, input):
#     """
#     This gives admins the ability to quiet a user.
#     The bot must be a Channel Operator for this command to work
#     """
#     if not input.admin:
#         return
#     text = input.group().split()
#     argc = len(text)
#     if argc < 2:
#         return
#     opt = text[1]
#     quietmask = opt
#     channel = input.sender
#     if opt.startswith('#'):
#         if argc < 3:
#             return
#         quietmask = text[2]
#         channel = opt
#     quietmask = configureHostMask(quietmask)
#     if quietmask == '':
#         return
#     code.write(['MODE', channel, '+q', quietmask])
# quiet.commands = ['quiet', 'mute']
# quiet.priority = 'high'


# def unquiet(code, input):
#     """
#     This gives admins the ability to unquiet a user.
#     The bot must be a Channel Operator for this command to work
#     """
#     if not input.admin:
#         return
#     text = input.group().split()
#     argc = len(text)
#     if argc < 2:
#         return
#     opt = text[1]
#     quietmask = opt
#     channel = input.sender
#     if opt.startswith('#'):
#         if argc < 3:
#             return
#         quietmask = text[2]
#         channel = opt
#     quietmask = configureHostMask(quietmask)
#     if quietmask == '':
#         return
#     code.write(['MODE', channel, '-q', quietmask])
# unquiet.commands = ['unquiet', 'unmute']
# unquiet.priority = 'high'


# def kickban(code, input):
#     """
#     This gives admins the ability to kickban a user.
#     The bot must be a Channel Operator for this command to work
#     .kickban [#chan] user1 user!*@* get out of here
#     """
#     if not input.admin:
#         return
#     text = input.group().split()
#     argc = len(text)
#     if argc < 4:
#         return
#     opt = text[1]
#     nick = opt
#     mask = text[2]
#     reasonidx = 3
#     if opt.startswith('#'):
#         if argc < 5:
#             eturn
#         channel = opt
#         nick = text[2]
#         mask = text[3]
#         reasonidx = 4
#     reason = ' '.join(text[reasonidx:])
#     mask = configureHostMask(mask)
#     if mask == '':
#         return
#     code.write(['MODE', channel, '+b', mask])
#     code.write(['KICK', channel, nick, ' :', reason])
# kickban.commands = ['kickban', 'kb']
# kickban.priority = 'high'


# def topic(code, input):
#     """
#     This gives admins the ability to change the topic.
#     Note: One does *NOT* have to be an OP, one just has to be on the list of
#     admins.
#     """
#     if not input.admin:
#         return
#     text = input.group().split()
#     topic = ' '.join(text[1:])
#     if topic == '':
#         return
#     code.write(['PRIVMSG', 'ChanServ'], 'TOPIC %s %s' % (input.sender, topic))
#     return
# topic.commands = ['topic']
# topic.priority = 'low'
