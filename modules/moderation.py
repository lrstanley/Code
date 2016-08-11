from random import choice as random
from util.hook import *
from util.tools import matchmask

# Todo:
#   - daemon/function to loop through all users, and kick and/or ban those that match
#     any bans.
#   - use the above, in conjunction with kick(), op(), voice(), etc to give the ability
#     to loop through all users and set permissions based on wildcard searching.
#     - MAKE SURE TO PUT DELAYS ON THIS.
#   - - Will be used for kickban


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


@hook(cmds=['ban', 'b', 'kickban'], trusted=True, ischannel=True, selfopped=True, args=True)
def ban(code, input):
    """ ban <user> - Bans a user from the current channel. Auto-kicks any users matching mask. """
    banmask = matchmask(input.group(2))
    if not banmask:
        return code.say('Invalid banmask! For more info, see: https://github.com/Liamraystanley/Code/wiki/Masks')
    return code.write(['MODE', input.sender, '+b', banmask])


@hook(cmds=['unban', 'ub'], trusted=True, ischannel=True, selfopped=True, args=True)
def unban(code, input):
    """ unban <user> - Unbans a user from the current channel. """
    banmask = matchmask(input.group(2))
    if not banmask:
        return code.say('Invalid banmask! For more info, see: https://github.com/Liamraystanley/Code/wiki/Masks')
    return code.write(['MODE', input.sender, '-b', banmask])


@hook(cmds=['topic'], trusted=True, ischannel=True, selfopped=True, args=True)
def topic(code, input):
    """ topic <text> - Sets the topic of the current channel to the given text. """
    code.write(['PRIVMSG', 'ChanServ'], 'TOPIC %s %s' % (input.sender, input.group(2)))
