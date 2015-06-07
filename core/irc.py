import re
import time
import traceback
import threading
import socket
import asyncore
import asynchat
import os
import sys
from util import output, database
from util.tools import convertmask
from util.web import uncharset, shorten
from core import triggers
from core.dispatch import dispatch


cwd = os.getcwd()


class Origin(object):
    source = re.compile(r'([^!]*)!?([^@]*)@?(.*)')

    def __init__(self, bot, source, args):
        match = Origin.source.match(source or '')
        self.nick, self.user, self.host = match.groups()

        if len(args) > 1:
            target = args[1]
        else:
            target = None

        mappings = {bot.nick: self.nick, None: None}
        self.sender = mappings.get(target, target)


class Bot(asynchat.async_chat):

    def __init__(self, nick, name, user, channels, server_password=None, debug=False):
        asynchat.async_chat.__init__(self)
        self.set_terminator('\n')
        self.buffer = ''
        self.id = 0
        self.nick = nick
        self.default = nick
        self.name = name
        self.user = user
        self.server_options = {}
        self.server_password = server_password
        self.channels = channels or list()
        self.stack = list()
        self.muted = False
        self.debug = debug
        self.irc_startup = None
        self.chan = {}
        self.bans = {}
        self.logs = {
            'bot': [],
            'channel': {}
        }
        self.special_chars = {
            'white': '\x0300', 'black': '\x0301', 'blue': '\x0302',
            'navy': '\x0302', 'green': '\x0303', 'red': '\x0304',
            'brown': '\x0305', 'maroon': '\x0305', 'purple': '\x0306',
            'orange': '\x0307', 'olive': '\x0307', 'gold': '\x0307',
            'yellow': '\x0308', 'lightgreen': '\x0309', 'lime': '\x0309',
            'teal': '\x0310', 'cyan': '\x0311', 'lightblue': '\x0312',
            'royal': '\x0312', 'lightpurple': '\x0313', 'pink': '\x0313',
            'fuchsia': '\x0313', 'grey': '\x0314', 'gray': '\x0314',
            'lightgrey': '\x0315', 'silver': '\x0315',
            # Even more special...
            'bold': '\x02', 'b': '\x02', 'italic': '\x1d', 'i': '\x1d',
            'reset': '\x0f', 'r': '\x0f', 'clear': '\x03', 'c': '\x03',
            'reverse': '\x16', 'underline': '\x1f', 'u': '\x1f'
        }

        # Load ignorelist
        self.blocks = database.get(self.nick, 'ignore', [])
        self.re_blocks = [convertmask(x) for x in self.blocks]

        self.sending = threading.RLock()

    def initiate_send(self):
        self.sending.acquire()
        asynchat.async_chat.initiate_send(self)
        self.sending.release()

    # def push(self, *args, **kargs):
    #    asynchat.async_chat.push(self, *args, **kargs)

    def run(self, id, host, port):
        self.id = id
        self.initiate_connect(host, port)

    def initiate_connect(self, host, port):
        output.normal('Connecting to %s:%s...' % (host, port), 'STATUS')
        try:
            # self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            source_address = ((self.config('bind_ip'), 0) if self.config('bind_ip') else None)
            self.set_socket(socket.create_connection((host, port), source_address=source_address))
            self.connect((host, port))
            asyncore.loop()
        except KeyboardInterrupt:
            os._exit(0)
        except Exception as e:
            output.error('Connection to %s:%s failed! (%s)' % (host, port, str(e)))
            os._exit(1)

    def handle_connect(self):
        self.irc_startup = int(time.time())
        output.success('Connected!', 'STATUS')
        if self.server_password:
            self.write(('PASS', self.server_password), output=False)
        self.write(('NICK', self.nick), output=False)
        self.write(('USER', self.user, '+iw', self.nick),
                   self.name, output=False)

    def handle_close(self):
        os._exit(1)

    def handle_error(self):
        '''Handle any uncaptured error in the core. Overrides asyncore's handle_error'''
        trace = traceback.format_exc()
        output.error('Fatal error in core, please review exception below:')
        output.error('Exception: ' + trace)

    def collect_incoming_data(self, data):
        self.buffer += data

    def found_terminator(self):
        line = self.buffer
        self.raw = line
        if line.endswith('\r'):
            line = line[:-1]
        self.buffer = ''

        if line.startswith(':'):
            source, line = line[1:].split(' ', 1)
        else:
            source = None

        if ' :' in line:
            argstr, text = line.split(' :', 1)
            args = argstr.split()
            args.append(text)
        else:
            args = line.split()
            text = args[-1]

        origin = Origin(self, source, args)

        if args[0] == 'PING':
            self.write(('PONG', text))
            return

        if self.debug:
            output.warning(repr(self.raw), 'DEBUG')

        try:
            if source and origin.nick != self.nick:
                getattr(triggers, 'trigger_%s' % args[0])(self, origin, line, args, text,)
        except AttributeError:
            pass
        except KeyError:
            pass

        # Execute this last so we know that out data is parsed first.
        # Slightly slower but we know we can get up-to-date information
        if args[0] == 'PRIVMSG':
            if self.muted and text[1::].split()[0].lower() not in ['unmute', 'help', 'mute']:
                return
        dispatch(self, origin, tuple([text] + args))

    def mute(self):
        self.muted = True

    def unmute(self):
        self.muted = False

    # def dispatch(self, origin, args):
    #     pass

    def error(self, origin, supress=False):
        try:
            trace = traceback.format_exc()
            output.error(trace)
            if supress:
                return
            lines = list(reversed(trace.splitlines()))
            report = [lines[0].strip()]
            for line in lines:
                line = line.strip()
                if line.startswith('File "/'):
                    report.append(line[0].lower() + line[1:])
                    break
            else:
                report.append('{red}Source unknown.{c}')

            self.msg(origin.sender, '{red}%s{c} ({b}%s{b})' % (report[0], report[1]))
        except:
            self.msg(origin.sender, '{red}Got an error.')

    def __write(self, args, text=None, raw=False):
        try:
            if raw:
                # temp = ' '.join(args)[:510] + ' :' + text + '\r\n'
                temp = args[:510] + '\r\n'
            elif not raw:
                if text:
                    # 510 because CR and LF count too
                    temp = (' '.join(args) + ' :' + text)[:510] + '\r\n'
                else:
                    temp = ' '.join(args)[:510] + '\r\n'
            self.push(temp)
            if self.debug and 'nickserv' not in temp.lower():
                output.warning(' > ' + temp, 'DEBUG')
        except IndexError:
            return

    def write(self, args, text=None, raw=False, output=True):
        try:
            args = [self.safe(arg, u=True) for arg in args]
            if text is not None:
                text = self.safe(text, u=True)
            if raw:
                self.__write(args, text, raw)
            else:
                self.__write(args, text)

            if args[0] == 'PRIVMSG':
                if args[1].startswith('#'):
                    self.add_logs(text, args[1], self.nick)
        except:
            pass
        try:
            getattr(triggers, 'trigger_write_%s' %
                    args[0])(self, args, text, raw,)
        except AttributeError:
            return
        except KeyError:
            pass

    def safe(self, input, u=False):
        """
            Strips the line endings and ensures the correct encoding before sending data
        """
        input = input.replace('\n', '').replace('\r', '')
        if u:
            try:
                input = input.encode('utf-8')
            except:
                pass
        return input

    def msg(self, recipient, text, x=False, shorten_urls=True, bypass_loop=False, colors=True):
        """
            Sends most messages to a direct location or recipient
            auto shortens URLs by default unless specified in the
            config
        """
        self.sending.acquire()
        if colors:
            text = self.format(text, shorten_urls=shorten_urls)

        if isinstance(text, unicode):
            try:
                text = text.encode('utf-8')
            except UnicodeEncodeError as e:
                text = e.__class__ + ': ' + str(e)
        if isinstance(recipient, unicode):
            try:
                recipient = recipient.encode('utf-8')
            except UnicodeEncodeError as e:
                return

        if not x:
            text = text.replace('\x01', '')

        # No messages within the last 3 seconds? Go ahead!
        # Otherwise, wait so it's been at least 0.5 seconds <nope>+ penalty</nope>
        if not bypass_loop:  # Used if you want to bypass the global rate limiter
            def wait(sk, txt):
                if sk:
                    elapsed = time.time() - sk[-1][0]
                    if elapsed < 3:
                        # penalty = float(max(0, len(txt) - 50)) / 70
                        wait = 0.5  # + penalty
                        if elapsed < wait:
                            time.sleep(wait - elapsed)

            wait(self.stack, text)

            # Loop detection
            messages = [m[1] for m in self.stack[-8:]]
            if messages.count(text) >= 5:
                text = '...'
                if messages.count('...') > 2:
                    self.sending.release()
                    return

        self.__write(('PRIVMSG', self.safe(recipient)), self.safe(text))
        output.normal('(%s) %s' %
                      (self.nick, self.stripcolors(self.clear_format(self.safe(text)))), self.safe(recipient))
        if self.safe(recipient).startswith('#') and self.safe(recipient) in self.logs['channel']:
            self.add_logs(text, recipient, self.nick)
        self.stack.append((time.time(), text))
        self.stack = self.stack[-10:]

        self.sending.release()

    def add_logs(self, text, channel, nick):
        """ Adds bot chat messages to the bot-central log dictionary """
        tmp = {
            'message': self.stripcolors(self.clear_format(self.safe(text))),
            'nick': self.nick,
            'time': int(time.time()),
            'channel': self.safe(channel)
        }
        # Remove ACTION's
        if '\x01ACTION' in tmp['message']:
            tmp['message'] = '(me) ' + \
                tmp['message'].replace('\x01', '').strip('ACTION')
        self.logs['channel'][self.safe(channel)].append(tmp)
        self.logs['bot'].append(tmp)

    def format(self, message, shorten_urls=True):
        '''
            formatting to support color/bold/italic/etc assignment
            and URL shortening in Codes responses
        '''
        message = uncharset(message)
        if self.config('shorten_urls') and shorten_urls:
            regex = re.compile(
                r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                re.IGNORECASE).findall(message)
            for url in regex:
                try:
                    message = message.replace(url, shorten(url))
                except:
                    pass
        if not self.config('text_decorations'):
            return self.clear_format(message)
        try:
            for special in self.special_chars:
                message = message.replace('{%s}' % special, self.special_chars[special])
            return message
        except:
            return self.clear_format(message)

    def clear_format(self, message):
        """ Cleans the custom made color parser (see above function) """
        find_char = re.compile(r'{.*?}')
        charlist = find_char.findall(message)
        for custom in charlist:
            message = message.replace(custom, '', 1)
        return message

    def stripcolors(self, data):
        """
            Note: the replacement method is CRUCIAL to keep from
            left over color digits. Order is very important.
        """
        colors = [
            u"\x0300", u"\x0301", u"\x0302", u"\x0303", u"\x0304", u"\x0305",
            u"\x0306", u"\x0307", u"\x0308", u"\x0309", u"\x0310", u"\x0311",
            u"\x0312", u"\x0313", u"\x0314", u"\x0315", u"\x031", u"\x032",
            u"\x033", u"\x034", u"\x035", u"\x036", u"\x037", u"\x038", u"\x039",
            u"\x030", u"\x03", u"\x02", u"\x09", u"\x13", u"\x0f", u"\x15"
        ]
        data = uncharset(data)
        for color in colors:
            try:
                data = data.replace(color, '')
            except:
                pass
        return str(data.encode('ascii', 'ignore'))

    def changenick(self, nick):
        """ Change the nickname of the bot """
        chars = set('`+=;,<>?')
        if not any((c in chars) for c in nick) and nick[0] != '-' and \
           len(nick) > 1 and len(nick) <= 20:
            self.write(('NICK', self.nick))
            self.nick = nick.encode('ascii', 'ignore')
            return True
        else:
            return None

    def notice(self, dest, text):
        """
            Send an IRC NOTICE to a user or a channel. See IRC protocol
            documentation for more information
        """
        text = self.format(text)
        self.write(('NOTICE', dest), text)

    def me(self, dest, text):
        """
            Send an action (/me) to a user or a channel.
            Keep in mind has to be "me" as a lambda action already exists
        """
        text = self.format(text)
        self.write(('PRIVMSG', dest), '\x01ACTION {}\x01'.format(text))

    def restart(self):
        """
            Reconnect to IRC and restart the bot process while keeping all other
            bot processes in tact and untouched
        """
        self.close()
        os._exit(1)

    def quit(self):
        """
            Disconnect from IRC and close the bot process while keeping other bot
            bot processes untouched. When using multi-network capability, you can
            terminate a single process without terminating the others
        """
        self.close()
        os._exit(0)

    def part(self, channel):
        """ Part a channel """
        self.write(['PART'], channel)

    def join(self, channel, password=None):
        """ Join a channel """
        output.info('Attempting to join channel %s' % channel, 'JOIN')
        try:
            channel = unicode(channel, 'utf-8')
        except:
            pass
        if password is None:
            self.write(['JOIN', channel])
        else:
            self.write(['JOIN', channel, password])

    def checkbans(self, channel):
        if not self.chan[channel][self.nick]['op']:
            return

        time.sleep(2)
        bans = []
        for mask in self.bans[channel]:
            mask = re.sub(r'(?i)^\${1,2}\:', '', mask)
            mask = re.sub(r'(?i)\#[A-Za-z]{1,2}$', '', mask)
            if mask != '*!*@*':
                bans.append(mask)

        re_bans = [convertmask(x) for x in bans]
        matchlist = []
        for nick in self.chan[channel]:
            ident, host = self.chan[channel][nick]['ident'], self.chan[channel][nick]['host']
            user = '{}!{}@{}'.format(nick, ident, host)
            match = [True if re.match(mask, user) else False for mask in re_bans]
            if True in match:
                matchlist.append([channel, nick])

        for channel, nick in matchlist:
            self.write(['KICK', channel, nick], 'Matching ban mask in %s' % channel)
            time.sleep(0.5)
