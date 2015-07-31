from util import output
import time
import os
from thread import start_new_thread as bg


def trigger_001(code, origin, line, args, text):
    """
        ID:         RPL_WELCOME
        Decription: The first message sent after client registration. The text used varies widely.
        Format:     Welcome to the Internet Relay Network <nick>!<user>@<host>
    """

    if not code.debug:
        output.normal('({}) {}'.format(origin.nick, text), 'NOTICE')


def trigger_002(code, origin, line, args, text):
    """
        ID:         RPL_YOURHOST
        Decription: Part of the post-registration greeting. Text varies.
                    widely
        Format:     Your host is <servername>, running version <version>
    """

    if not code.debug:
        output.normal('({}) {}'.format(origin.nick, text), 'NOTICE')


def trigger_003(code, origin, line, args, text):
    """
        ID:         RPL_CREATED
        Decription: Part of the post-registration greeting. Text varies widely.
        Format:     This server was created <date>
    """

    output.normal('({}) {}'.format(origin.nick, text), 'NOTICE')


def trigger_004(code, origin, line, args, text):
    """
        ID:         RPL_MYINFO
        Decription: Part of the post-registration greeting. Text varies widely.
        Format:     <server_name> <version> <user_modes> <chan_modes>
    """

    code.server_options['SERVERNAME'] = args[2]
    # As this varies widely, I should check to see if it exists first...
    # Will implement a different fix using VERSION at a later time.
    code.server_options['VERSION'] = args[3] if len(args) >= 4 else ''
    code.server_options['UMODES'] = args[4] if len(args) >= 5 else ''
    code.server_options['CMODES'] = args[5] if len(args) >= 6 else ''


def trigger_005(code, origin, line, args, text):
    """
        ID:         RPL_ISUPPORT
        Decription: Also known as RPL_PROTOCTL (Bahamut, Unreal, Ultimate).
    """

    tmp = args[2:-1]
    for item in tmp:
        if '=' not in item:
            code.server_options[item] = True
        else:
            name, data = item.split('=', 1)
            code.server_options[name] = data


def trigger_250(code, origin, line, args, text):
    """
        ID: RPL_STATSCONN
    """

    if not code.debug:
        output.normal('({}) {}'.format(origin.nick, text), 'NOTICE')


def trigger_251(code, origin, line, args, text):
    """
        ID:         RPL_LUSERCLIENT
        Decription: Reply to LUSERS command, other versions exist (eg. RFC2812); Text may vary.
        Format:     There are <int> users and <int> invisible on <int> servers
    """

    if code.config('nickserv_password'):
        if code.config('nickserv_username'):
            args = code.config('nickserv_username') + ' ' + code.config('nickserv_password')
        else:
            args = code.config('nickserv_password')
        if code.config('nickserv_is_x'):
            code.write(['PRIVMSG', 'x@channels.undernet.org'], 'login %s' % args, output=False)
        else:
            code.write(['PRIVMSG', 'NickServ'], 'IDENTIFY %s' % args, output=False)
        time.sleep(5)

    # Wait 5 seconds to ensure that the bot is authenticated before attempting to join any channels or set any modes.
    time.sleep(5)

    # Assume it's for bots, y'know
    code.write(('MODE', code.nick, '+B'))

    for channel in code.channels:
        code.join(channel)
        code.write(['WHO', channel, '%tcuhn,1'])
        time.sleep(0.5)

    def sendping(code):
        while True:
            try:
                code.write(('PING', 'Code'))
            except Exception as e:
                if code.debug:
                    output.error('Error while pinging server. (%s)' % str(e))
            time.sleep(int(float(code.irc_timeout) / 3))

    def checkping(code):
        while True:
            try:
                diff = int(time.time()) - code.lastping
                if diff > code.irc_timeout:
                    output.warning("Connection from IRC timed out after %s seconds, initiating reconnect..." % code.irc_timeout)
                    code.restart()
            except:
                pass
            time.sleep(5)

    bg(sendping, (code,))
    bg(checkping, (code,))

    return trigger_250(code, origin, line, args, text)


def trigger_255(code, origin, line, args, text):
    """
        ID:         RPL_LUSERME
        Decription: Reply to LUSERS command - Information about local connections; Text may vary.
        Format:     I have <int> clients and <int> servers
    """

    return trigger_250(code, origin, line, args, text)


def trigger_352(code, origin, line, args, text):
    """
        ID:         RPL_WHOREPLY
        Decription: Reply to vanilla WHO (See RFC). This format can be very different if the 'WHOX'
                    version of the command is used (see ircu).
        Format:     <channel> <user> <host> <server> <nick> <H|G>[*][@|+] :<hopcount> <real_name>
    """

    return trigger_354(code, origin, line, args, text, is_352=True)


def trigger_353(code, origin, line, args, text):
    """
        ID:         RPL_NAMREPLY
        Decription: Reply to NAMES (See RFC)
        Format:     ( '=' / '*' / '@' ) <channel> ' ' : [ '@' / '+' ] <nick> *( ' ' [ '@' / '+' ] <nick> )
    """

    channel, user_list = args[3], args[4]
    channel, user_list = '#' + \
        channel.split('#', 1)[1].strip(), user_list.strip().split()
    if channel not in code.chan:
        code.chan[channel] = {}
    if channel not in code.bans:
        code.bans[channel] = []
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
        code.chan[channel][name] = {'normal': normal, 'voiced': voiced, 'op': op, 'count': 0, 'messages': []}


def trigger_354(code, origin, line, args, text, is_352=False):
    """
        ID:         RPL_WHOSPCRPL
        Decription: Reply to WHO, however it is a 'special' reply because it is returned using a
                    non-standard (non-RFC1459) format. The format is dictated by the command given
                    by the user, and can vary widely. When this is used, the WHO command was invoked
                    in its 'extended' form, as announced by the 'WHOX' ISUPPORT tag.
    """

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


def trigger_367(code, origin, line, args, text):
    """
        ID:         RPL_BANLIST
        Decription: A ban-list item (See RFC); <time left> and <reason> are additions used by
                    KineIRCd
        Format:     <channel> <banid> [<time_left> :<reason>]
    """

    code.bans[args[2]].append(args[3])


def trigger_368(code, origin, line, args, text):
    """
        ID:         RPL_ENDOFBANLIST
        Decription: Termination of an RPL_BANLIST list
        Format:     <channel> :<info>
    """
    return code.checkbans(args[2])


def trigger_433(code, origin, line, args, text):
    """
        ID:         ERR_NICKNAMEINUSE
        Decription: Returned by the NICK command when the given nickname is already in use
        Format:     <nick> :<reason>
    """

    if not code.debug:
        output.warning('Nickname {} is already in use. Trying another..'.format(code.nick))
    nick = code.nick + '_'
    code.write(('NICK', nick))
    code.nick = nick.encode('ascii', 'ignore')


def trigger_437(code, origin, line, args, text):
    """
        ID:         ERR_UNAVAILRESOURCE
        Decription: Return when the target is unable to be reached temporarily, eg. a delay
                    mechanism in play, or a service being offline
        Format:     <nick/channel/service> :<reason>
    """

    if not code.debug:
        output.error(text)
    os._exit(1)


def trigger_471(code, origin, line, args, text):
    """
        ID:         ERR_CHANNELISFULL
        Decription: Returned when attempting to join a channel which is set +l and is already
                    full
        Format:     <channel> :<reason>
    """

    return output.error(args[3], args[2])


def trigger_473(code, origin, line, args, text):
    """
        ID:         ERR_INVITEONLYCHAN
        Decription: Returned when attempting to join a channel which is invite only without an
                    invitation
        Format:     <channel> :<reason>
    """

    return output.error(args[3], args[2])


def trigger_474(code, origin, line, args, text):
    """
        ID:         ERR_BANNEDFROMCHAN
        Decription: Returned when attempting to join a channel a user is banned from
        Format:     <channel> :<reason>
    """

    return output.error(args[3], args[2])


def trigger_475(code, origin, line, args, text):
    """
        ID:         ERR_BADCHANNELKEY
        Decription: Returned when attempting to join a key-locked channel either without a
                    key or with the wrong key
        Format:     <channel> :<reason>
    """

    return output.error(args[3], args[2])


def trigger_NICK(code, origin, line, args, text):
    """
        ID:         NICK
        Decription: NICK message is used to give user a nickname or change the previous
                    one. The <hopcount> parameter is only used by servers to indicate
                    how far away a nick is from its home server. A local connection has
                    a hopcount of 0. If supplied by a client, it must be ignored.

        Format:     <nickname> [ <hopcount> ]
        Numeric Replies:
           - ERR_NONICKNAMEGIVEN
           - ERR_ERRONEUSNICKNAME
           - ERR_NICKNAMEINUSE
           - ERR_NICKCOLLISION
    """

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
    """
        ID:         PRIVMSG
        Decription: PRIVMSG is used to send private messages between users. <receiver>
                    is the nickname of the receiver of the message. <receiver> can also
                    be a list of names or channels separated with commas.
        Format:     <receiver>{,<receiver>} :<text to be sent>
        Numeric Replies:
           - ERR_NORECIPIENT
           - ERR_NOTEXTTOSEND
           - ERR_CANNOTSENDTOCHAN
           - ERR_NOTOPLEVEL
           - ERR_WILDTOPLEVEL
           - ERR_TOOMANYTARGETS
           - ERR_NOSUCHNICK
           - RPL_AWAY
    """

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
    """
        ID:         NOTICE
        Decription: The NOTICE message is used similarly to PRIVMSG. The difference
                    between NOTICE and PRIVMSG is that automatic replies must never be
                    sent in response to a NOTICE message. This rule applies to servers
                    too - they must not send any error reply back to the client on
                    receipt of a notice.
        Format:     <nickname> <text>
    """

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
    """
        ID:         KICK
        Decription: The KICK command can be used to forcibly remove a user from a
                    channel. It 'kicks them out' of the channel (forced PART).
        Format:     <channel> <user> [<comment>]
    """

    output.normal('{} has kicked {} from {}. Reason: {}'.format(
        origin.nick, args[2], args[1], args[3]), 'KICK', 'red')
    del code.chan[args[1]][args[2]]


def trigger_write_KICK(code, args, text, raw):
    output.normal('I have kicked {} from {}'.format(args[2], args[1]), 'KICK', 'red')
    if args[2] in code.chan[args[1]]:
        del code.chan[args[1]][args[2]]


def trigger_MODE(code, origin, line, args, text):
    """
        ID:         MODE
        Decription: The MODE command is a dual-purpose command in IRC. It allows both
                    usernames and channels to have their mode changed. The rationale for
                    this choice is that one day nicknames will be obsolete and the
                    equivalent property will be the channel.

                    When parsing MODE messages, it is recommended that the entire message
                    be parsed first and then the changes which resulted then passed on.
        Format:     <channel> {[+|-]|o|p|s|i|t|n|b|v} [<limit>] [<user>] [<ban mask>]
                    <nickname> {[+|-]|i|w|s|o}
    """
    if len(args) == 4:
        if args[1].startswith('#') and '+b' in args:
            code.bans[args[1]] = []
            code.write(['MODE', args[1], '+b'])

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
            mode, name, sign = names[user['mode']], user['name'], names[user['sign']]
            code.chan[channel][name][mode] = sign
            if mode == 'op' and sign:
                code.chan[channel][name]['voiced'] = True


def trigger_write_MODE(code, args, text, raw):
    """
        ID:         MODE
        Decription: Triggered when the bot write a MODE +b, so that we can list all
                    bans, and kick users evading
    """
    if len(args) < 4:
        return
    if not args[1].startswith('#') and '+b' not in args:
        return
    code.bans[args[1]] = []
    code.write(['MODE', args[1], '+b'])


def trigger_JOIN(code, origin, line, args, text):
    """
        ID:         JOIN
        Decription: The JOIN command is used by client to start listening a specific
                    channel. Whether or not a client is allowed to join a channel is
                    checked only by the server the client is connected to; all other
                    servers automatically add the user to the channel when it is received
                    from other servers.  The conditions which affect this are as follows:
                        1.  the user must be invited if the channel is invite-only;
        Format:     <channel>{,<channel>} [<key>{,<key>}]
    """

    if origin.nick != code.nick:
        code.chan[args[1]][origin.nick] = {'normal': True, 'voiced': False, 'op': False, 'count': 0, 'messages': []}
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
    """
        ID:         PART
        Decription: The PART message causes the client sending the message to be removed
                    from the list of active users for all given channels listed in the
                    parameter string.
        Format:     <channel>{,<channel>}
        Numeric Replies:
           - ERR_NEEDMOREPARAMS
           - ERR_NOSUCHCHANNEL
           - ERR_NOTONCHANNEL
    """

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
    """
        ID:         PART
        Decription: Triggered when the bot write a PART, so that we can unhook
                    database from that channel.
        Format: part <channel>
    """

    del code.chan[args[1]]
    del code.logs['channel'][args[1]]
    del code.chan[args[1]]


def trigger_QUIT(code, origin, line, args, text):
    """
        ID:         QUIT
        Decription: A client session is ended with a quit message. The server must close
                    the connection to a client which sends a QUIT message. If a "Quit
                    Message" is given, this will be sent instead of the default message,
                    the nickname. When netsplits (disconnecting of two servers) occur, the quit message
                    is composed of the names of two servers involved, separated by a
                    space. The first name is that of the server which is still connected
                    and the second name is that of the server that has become
                    disconnected.
        Format:     [<Quit message>]
    """

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
