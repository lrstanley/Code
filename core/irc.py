#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
irc.py - Code A Utility IRC Bot
https://www.liamstanley.io/Code.git
"""

import re
import time
import traceback
import threading
import socket
import asyncore
import asynchat
import os
from util import output
from util.web import uncharset
from util.web import shorten
from core import triggers


IRC_CODES = (
    '251', '252', '254', '255', '265', '266', '250', '333', '353', '366',
    '372', '375', '376', 'QUIT', 'NICK'
)
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

        self.nick = nick
        self.name = name
        self.user = user
        self.server_password = server_password

        self.verbose = True
        self.channels = channels or list()
        self.stack = list()
        self.debug = debug
        self.chan = {}
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
            'bold': '\x02', 'b': '\x02', 'italic': '\x16', 'underline': '\x1f',
            'reset': '\x0f', 'r': '\x0f', 'clear': '\x03', 'c': '\x03'
        }

        self.sending = threading.RLock()

    def initiate_send(self):
        self.sending.acquire()
        asynchat.async_chat.initiate_send(self)
        self.sending.release()

    # def push(self, *args, **kargs):
    #    asynchat.async_chat.push(self, *args, **kargs)

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
            message = message.format(**self.special_chars)
            return message
        except:
            return self.clear_format(message)

    def clear_format(self, message):
        find_char = re.compile(r'{.*?}')
        charlist = find_char.findall(message)
        for custom in charlist:
            message = message.replace(custom, '', 1)
        return message

    def quit(self, message=None):
        '''Disconnect from IRC and close the bot'''
        if not message:
            message = 'Terminating Code.'
        self.write(['QUIT'], message)
        self.hasquit = True
        __import__('os')._exit(0)

    def part(self, channel):
        '''Part a channel'''
        self.write(['PART'], channel)

    def join(self, channel, password=None):
        '''Join a channel'''
        output.info('Attempting to join channel %s' % channel, 'JOIN')
        try:
            channel = unicode(channel, 'utf-8')
        except:
            pass
        if password is None:
            self.write(['JOIN', channel])
        else:
            self.write(['JOIN', channel, password])

    def __write(self, args, text=None, raw=False):
        try:
            if raw:
                temp = ' '.join(args)[:510] + ' :' + text + '\r\n'
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
        # output isn't used /yet/
        try:
            args = [self.safe(arg, u=True) for arg in args]
            if text is not None:
                text = self.safe(text, u=True)
            if raw:
                self.__write(args, text, raw)
            else:
                self.__write(args, text)
        except:
            pass

    def safe(self, input, u=False):
        if input:
            input = input.replace('\n', '').replace('\r', '')
            if u:
                input = input.encode('utf-8')
        return input

    def run(self, host, port):
        self.initiate_connect(host, port)

    def initiate_connect(self, host, port):
        count = 0
        max_attempts = 5
        if self.config('connect_delay'):
            delay = int(self.config('connect_delay'))
        else:
            delay = 20
        while True:
            if count >= max_attempts:
                break
            try:
                count += 1
                if count > 1:
                    output.error(
                        'Failed to connect! Trying again in '
                        '%s seconds.' % str(delay)
                    )
                    time.sleep(delay)
                if self.verbose:
                    output.normal('Connecting to %s:%s... (try %s)' %
                                  (host, port, str(count)), 'STATUS')
                self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connect((host, port))
                count = 0
                asyncore.loop()
            except:
                pass
        output.error('Too many failed attempts. Exiting.')
        os._exit(1)

    def handle_connect(self):
        if self.verbose:
            output.success('Connected!', 'STATUS')
        if self.server_password:
            self.write(('PASS', self.server_password), output=False)
        self.write(('NICK', self.nick), output=False)
        self.write(('USER', self.user, '+iw', self.nick),
                   self.name, output=False)

    def changenick(self, nick):
        chars = set('`+=;,<>?')
        if not any((c in chars) for c in nick) and nick[0] != '-' and \
           len(nick) > 1 and len(nick) <= 20:
            self.write(('NICK', self.nick))
            self.nick = nick.encode('ascii', 'ignore')
            # we can't tell yet if the
            # nick successfully changed,
            # so this variable will get
            # messed up, if unsuccessful.
            return True
        else:
            return None

    def handle_close(self):
        self.close()
        output.error('Disconnected from IRC - Reason unknown!')

    def handle_error(self):
        '''Handle any uncaptured error in the core. Overrides asyncore's handle_error'''
        trace = traceback.format_exc()
        output.error('Fatal error in core, please review exception below:')
        output.error('Exception: ' + trace)

    def collect_incoming_data(self, data):
        self.buffer += data
        if not data:
            return

        if self.debug:
            output.warning(data, 'DEBUG')

        self.raw = data.replace('\x02', '').replace('\r', '')
        line = self.raw.strip()

        if not line.startswith(':'):
            return

        try:
            if line[1::].split()[0] == self.nick:
                return

            code = line.split()[1]
            getattr(triggers, 'trigger_%s' % code)(self, line,)
        except (AttributeError, IndexError, KeyError):
            return

    def stripcolors(self, data):
        """STRIP ALL ZE COLORS! Note: the replacement method is CRUCIAL to keep from
           left over color digits. Order is very important."""
        colors = [
            u"\x0300", u"\x0301", u"\x0302", u"\x0303", u"\x0304", u"\x0305",
            u"\x0306", u"\x0307", u"\x0308", u"\x0309", u"\x0310", u"\x0311",
            u"\x0312", u"\x0313", u"\x0314", u"\x0315", u"\x031", u"\x032",
            u"\x033", u"\x034", u"\x035", u"\x036", u"\x037", u"\x038", u"\x039",
            u"\x030", u"\x03", u"\x02", u"\x09", u"\x13", u"\x0f", u"\x15"
        ]
        data = uncharset(data)
        for color in colors:
            data = data.replace(color, '')
        return str(data.encode('ascii', 'ignore'))

    def found_terminator(self):
        line = self.buffer
        if line.endswith('\r'):
            line = line[:-1]
        self.buffer = ''

        # print line
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
        self.dispatch(origin, tuple([text] + args))

        if args[0] == 'PING':
            self.write(('PONG', text))

    def dispatch(self, origin, args):
        pass

    def msg(self, recipient, text, x=False, shorten_urls=True):
        self.sending.acquire()
        text = self.format(text, shorten_urls=shorten_urls)

        if isinstance(text, unicode):
            try:
                text = text.encode('utf-8')
            except UnicodeEncodeError, e:
                text = e.__class__ + ': ' + str(e)
        if isinstance(recipient, unicode):
            try:
                recipient = recipient.encode('utf-8')
            except UnicodeEncodeError, e:
                return

        if not x:
            text = text.replace('\x01', '')

        # No messages within the last 3 seconds? Go ahead!
        # Otherwise, wait so it's been at least 0.8 seconds + penalty
        def wait(sk, txt):
            if sk:
                elapsed = time.time() - sk[-1][0]
                if elapsed < 3:
                    penalty = float(max(0, len(txt) - 50)) / 70
                    wait = 0.8 + penalty
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
        self.stack.append((time.time(), text))
        self.stack = self.stack[-10:]

        self.sending.release()

    def notice(self, dest, text):
        '''Send an IRC NOTICE to a user or a channel. See IRC protocol
           documentation for more information'''
        text = self.format(text)
        self.write(('NOTICE', dest), text)

    def action(self, dest, text):
        '''Send an action (/me) to a user or a channel'''
        text = self.format(text)
        self.write(('PRIVMSG', dest), '\x01ACTION ' + text + '\x01')

    def error(self, origin):
        try:
            # import traceback
            trace = traceback.format_exc()
            output.error(trace)
            lines = list(reversed(trace.splitlines()))
            report = [lines[0].strip()]
            for line in lines:
                line = line.strip()
                if line.startswith('File "/'):
                    report.append(line[0].lower() + line[1:])
                    break
            else:
                report.append('{red}Source unknown.')

            self.msg(origin.sender, report[0] + ' (' + report[1] + ')')
        except:
            self.msg(origin.sender, '{red}Got an error.')
