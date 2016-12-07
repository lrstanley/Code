import os
import time
from util.hook import *
from util import output
from util import database
from util.tools import matchmask, convertmask
from thread import start_new_thread as daemonize

defaultnick = None
auto_voice_timer = 3600  # in seconds


def setup(code):
    if not code.config('voice_active_users'):
        return
    output.info('Starting daemon', 'AUTOVOICE')
    daemonize(auto_voice, (code,))


def auto_voice(code):
    while True:
        time.sleep(5)
        try:
            if code.debug:
                output.info('Running check', 'AUTOVOICE')
            for channel in code.config('voice_active_users'):
                if channel not in code.chan:
                    continue
                if not code.chan[channel][code.nick]['op']:
                    continue
                for user in code.chan[channel]:
                    if user == code.nick:  # It's the bot lel
                        continue
                    # Ignore if they're op. They pretty much have voice.. lol
                    if code.chan[channel][user]['op'] is True:
                        continue
                    current_time = int(time.time())
                    # Ignore if they haven't said anything...
                    if code.chan[channel][user]['count'] == 0:
                        last_msg_time = 0
                    else:
                        last_msg_time = int(code.chan[channel][user]['messages'][-1]['time'])
                    difference = current_time - last_msg_time  # How long ago did they say something
                    first_joined_difference = current_time - code.chan[channel][user]['first_seen']  # How long
                    # has it been since we first saw them...
                    if difference > auto_voice_timer:
                        # It's been longer than the timer..
                        # If they're voiced, devoice
                        # However, to prevent from a load of users being devoiced when the bot joins
                        # Check for the first-seen-time
                        if code.chan[channel][user]['voiced'] and auto_voice_timer < first_joined_difference:
                            code.chan[channel][user]['voiced'] = False
                            code.write(('MODE', channel, '-v', user))
                    else:
                        # It's shorter... voice if not voiced..
                        if not code.chan[channel][user]['voiced']:
                            code.chan[channel][user]['voiced'] = True
                            code.write(('MODE', channel, '+v', user))
        except:
            continue


@hook(cmds=['modules'], rate=20, priority='high', admin=True)
def listmods(code, input):
    """ modules - Send a list of the loaded modules to the user. """
    return code.say('{b}Modules: {r}%s.' % ', '.join(code.modules))


@hook(cmds=['join'], ex='join #example key', admin=True, args=True)
def join(code, input):
    """ join <#channel> [key] - Join the specified channel. Admin only. """
    if not input.group(2).startswith("#"):
        return error(code)
    if len(input.group(2).split()) > 1:  # Channel + key
        return code.write(['JOIN', input.group(2).split(' ', 1)])
    else:
        return code.write(['JOIN'], input.group(2).strip())


@hook(cmds=['part', 'leave'], ex='part #example', admin=True, args=True)
def part(code, input):
    """ part <#channel> - Part the specified channel. Admin only. """
    if not input.group(2).startswith("#"):
        return error(code)
    return code.write(['PART', input.group(2).strip()])


@hook(cmds=['restart', 'reboot', 'reconnect'], admin=True)
def restart(code, input):
    """ restart - Reconnect to the server. (Fully restarts the server process) Admin only. """
    code.restart()


@hook(cmds=['quit', 'disconnect', 'shutdown', 'stop'], owner=True)
def quit(code, input):
    """ quit - Quit from the server. Owner only. """
    code.quit()


@hook(cmds=['name', 'nick', 'nickname'], priority='low', owner=True, args=True)
def nick(code, input):
    """ Change nickname dynamically. Owner only. """
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
    """ msg <channel|username> <msg> - Send a message to a channel, or a user. Admin-only. """
    if len(input.group(2).split()) < 2:
        return code.say('{red}{b}Incorrect usage!: %smsg <channel|username> <msg>' % code.prefix)
    a, b = input.group(2).split(' ', 1)
    if not input.owner and a.lower() in ['chanserv', 'nickserv', 'hostserv', 'memoserv', 'saslserv', 'operserv']:
        return code.say('{red}{b}You\'re not authorized to message those services!')
    code.msg(a, b)


@hook(cmds=['me', 'action'], ex='me #L loves Liam', priority='low', admin=True, args=True)
def me(code, input):
    """ me <channel|username> <msg> - Send a raw ACTION to a channel/user. Admin-only. """
    msg = input.group(2)
    if len(msg.split()) < 2:
        return code.say('{red}{b}Incorrect usage!: %saction <channel|username> <msg>' % code.prefix)
    msg = msg.split(' ', 1)
    code.me(msg[0], msg[1])


@hook(cmds=['notice'], ex='notice #L Thie bot is awesome!', priority='low', admin=True, args=True)
def notice(code, input):
    """ notice <channel|username> <msg> - Send a raw NOTICE to a channel/user. Admin-only. """
    msg = input.group(2)
    if len(msg.split()) < 2:
        return code.say('{red}{b}Incorrect usage!: %snotice <channel|username> <msg>' % code.prefix)
    msg = msg.split(' ', 1)
    code.notice(msg[0], msg[1])


@hook(cmds=['announce', 'broadcast'], ex='announce Some important message here', priority='low', admin=True, args=True)
def announce(code, input):
    """ announce <message> - Send an announcement to all channels the bot is in """
    for channel in code.channels:
        code.msg(channel, '{b}{purple}[ANNOUNCMENT] %s' % input.group(2), bypass_loop=True)


@hook(cmds=['block', 'ignore'], ex='ignore Spammer*!*@spammy.server-101.net', thread=False, admin=True, args=True)
def ignore(code, input):
    """ ignore <mask> - Makes code ignore anyone matching <mask> """
    mask = matchmask(input.group(2))
    if not mask:
        return code.say('Invalid mask! For more info, see: https://github.com/lrstanley/Code/wiki/Masks')
    blocks = database.get(code.nick, 'ignore', [])
    if mask not in blocks:
        blocks.append(mask)
    else:
        return code.say('%s is already in the ignorelist!' % mask)
    code.blocks = blocks
    code.re_blocks = [convertmask(x) for x in blocks]
    database.set(code.nick, blocks, 'ignore')
    return code.say('Successfully added %s to the ignore list.' % mask)


@hook(cmds=['unblock', 'unignore'], ex='unignore MaybeNotSpammer*!*@spammy.server-101.net', thread=False, admin=True, args=True)
def unignore(code, input):
    """ unignore <mask> - Removes <mask> from ignore list. """
    mask = matchmask(input.group(2))
    if not mask:
        return code.say('Invalid mask! For more info, see: https://github.com/lrstanley/Code/wiki/Masks')
    blocks = database.get(code.nick, 'ignore', [])
    if mask not in blocks:
        return code.say('%s doesn\'t exist in the ignore list!' % mask)
    del blocks[blocks.index(mask)]
    code.blocks = blocks
    code.blocks = [convertmask(x) for x in blocks]
    database.set(code.nick, blocks, 'ignore')
    return code.say('Successfully removed %s from the ignore list.' % mask)


@hook(cmds=['blocklist', 'bl', 'ignorelist', 'il'], thread=False, admin=True)
def ignorelist(code, input):
    """ ignorelist - Lists ignorelist. """
    blocks = database.get(code.nick, 'ignore', [])
    return code.say('"{b}%s{b}"' % '{b}", "{b}'.join(blocks))


@hook(cmds=['write', 'raw'], priority='high', thread=False, owner=True, args=True)
def write_raw(code, input):
    """ write <args> - Send a raw command to the server. WARNING THIS IS DANGEROUS! Owner-only. """
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
