#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
irc.py - Code A Utility IRC Bot
http://code.liamstanley.io/
"""

import sys, re, time, traceback
import socket, asyncore, asynchat
import os, codecs
from util import output

IRC_CODES = ('251', '252', '254', '255', '265', '266', '250', '333', '353', '366', '372', '375', '376', 'QUIT', 'NICK')
cwd = os.getcwd()

class Origin(object):
    source = re.compile(r'([^!]*)!?([^@]*)@?(.*)')

    def __init__(self, bot, source, args):
        match = Origin.source.match(source or '')
        self.nick, self.user, self.host = match.groups()

        if len(args) > 1:
            target = args[1]
        else: target = None

        mappings = {bot.nick: self.nick, None: None}
        self.sender = mappings.get(target, target)

def create_logdir():
    try: os.mkdir(cwd + '/logs')
    except Exception, e:
        output.error('There was a problem creating the logs directory.')
        output.error(e.__class__, str(e))
        output.error('Please fix this and then run code again.')
        sys.exit(1)

def check_logdir():
    if not os.path.isdir(cwd + '/logs'):
        create_logdir()

def log_raw(line):
    check_logdir()
    f = codecs.open(cwd + '/logs/raw.log', 'a', encoding='utf-8')
    f.write(str(time.time()) + "\t")
    temp = line.replace('\n', '')
    try:
        temp = temp.decode('utf-8')
    except UnicodeDecodeError:
        try:
            temp = temp.decode('iso-8859-1')
        except UnicodeDecodeError:
            temp = temp.decode('cp1252')
    f.write(temp)
    f.write('\n')
    f.close()

class Bot(asynchat.async_chat):
    def __init__(self, nick, name, channels, serverpass=None, logchan_pm=None, logging=False):
        asynchat.async_chat.__init__(self)
        self.set_terminator('\n')
        self.buffer = ''

        self.nick = nick
        self.user = 'code'
        self.name = name
        self.serverpass = serverpass

        self.verbose = True
        self.channels = channels or list()
        self.stack = list()
        self.stack_log = list()
        self.logchan_pm = logchan_pm
        self.logging = logging
        self.chan = {}
        self.special_chars = {
            'white': '\x0300', 'black': '\x0301', 'blue': '\x0302', 'navy': '\x0302',
            'green': '\x0303', 'red': '\x0304', 'brown': '\x0305', 'maroon': '\x0305',
            'purple': '\x0306', 'orange': '\x0307', 'olive': '\x0307', 'gold': '\x0307',
            'yellow': '\x0308', 'lightgreen': '\x0309', 'lime': '\x0309', 'teal': '\x0310',
            'cyan': '\x0311', 'lightblue': '\x0312', 'royal': '\x0312', 'lightpurple': '\x0313',
            'pink': '\x0313', 'fuchsia': '\x0313', 'grey': '\x0314', 'lightgrey': '\x0315',
            'silver': '\x0315',
            # Even more special...
            'bold': '\x02', 'b': '\x02', 'italic': '\x16', 'underline': '\x1f', 'reset': '\x0f',
            'r': '\x0f', 'clear': '\x03', 'c': '\x03'
        }

        import threading
        self.sending = threading.RLock()

    #def push(self, *args, **kargs):
    #    asynchat.async_chat.push(self, *args, **kargs)

    def format(self, message, legacy=None):
        '''formatting to support color/bold/italic/etc assignment in Codes responses'''
        if not hasattr(self.config, 'textstyles'):
            return message
        if not self.config.textstyles:
            return message
        if legacy:
            message = '{%s}%s{%s}' % (legacy, message, legacy)
        find_char = re.compile(r'{.*?}')
        charlist = find_char.findall(unicode(message))
        try:
            message = unicode(message)

            for formatted_char in charlist:
                char = formatted_char[1:-1]
                if char.startswith('/'):
                    char = char[1::] # Assume closing {/char}
                if char in self.special_chars:
                    message = message.replace(formatted_char, self.special_chars[char],1)
            return message
        except:
            for custom in charlist:
                message = message.replace(custom,'',1)
            return message


    def color(self, color, message):
        return self.format(message, color)

    def bold(self, message):
        return self.format(message, 'bold')
            
    def italic(self, message):
        return self.format(message, 'italic')

    def underline(self, message):
        return self.format(message, 'underline')

    def quit(self, message=None):
        '''Disconnect from IRC and close the bot'''
        if not message: message = 'Terminating Code.'
        self.write(['QUIT'], message)
        self.hasquit = True
        __import__('os')._exit(0)

    def part(self, channel):
        '''Part a channel'''
        self.write(['PART'], channel)

    def join(self, channel, password=None):
        '''Join a channel'''
        output.info('Attempting to join channel %s' % channel, 'JOIN')
        if password is None:
            self.write(['JOIN', channel])
        else:
            self.write(['JOIN', channel, password])

    def __write(self, args, text=None, raw=False):
        #print '[WRITE] %r %r' % (args, text)
        # Not needed anymore
        try:
            if raw:
                temp = ' '.join(args)[:510] + ' :' + text + '\r\n'
            elif not raw:
                if text:
                    # 510 because CR and LF count too, as nyuszika7h points out
                    temp = (' '.join(args) + ' :' + text)[:510] + '\r\n'
                else:
                    temp = ' '.join(args)[:510] + '\r\n'
            self.push(temp)
            if self.logging:
                log_raw(temp)
        except IndexError:
            return

    def write(self, args, text=None, raw=False):
        try:
            args = [self.safe(arg, u=True) for arg in args]
            if text is not None:
                text = self.safe(text, u=True)
            if raw:
                self.__write(args, text, raw)
            else:
                self.__write(args, text)
        except Exception, e: pass

    def safe(self, input, u=False):
        if input:
            input = input.replace('\n', '').replace('\r', '')
            if u:
                input = input.encode('utf-8')
        return input

    def run(self, host, port=6667):
        self.initiate_connect(host, port)

    def initiate_connect(self, host, port):
        if self.verbose:
            output.normal('Connecting to %s:%s...' % (host, port), 'STATUS')
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
        try: asyncore.loop()
        except KeyboardInterrupt:
            sys.exit()

    def handle_connect(self):
        if self.verbose:
            output.success('Connected!', 'STATUS')
        if self.serverpass:
            self.write(('PASS', self.serverpass))
        self.write(('NICK', self.nick))
        self.write(('USER', self.user, '+iw', self.nick), self.name)

    def changenick(self, nick):
        chars = set('`+=;,<>?')
        if not any((c in chars) for c in nick) and nick[0] != '-' and \
        len(nick) > 1 and len(nick) <= 20:
            self.write(('NICK', self.nick))
            self.nick = nick.encode('ascii','ignore') # we can't tell yet if the
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
        try:
            output.error(trace)
        except:
            pass
        output.error('Fatal error in core, please review exception below:')
        output.error('Exception: ' + trace)

    def collect_incoming_data(self, data):
        self.buffer += data
        if data:
            if self.logchan_pm:
                dlist = data.split()
                if len(dlist) >= 3:
                    if '#' not in dlist[2] and dlist[1].strip() not in IRC_CODES:
                        self.msg(self.logchan_pm, data, True)
            if self.logging:
                log_raw(data)
            self.raw = data.replace('\x02','').replace('\r','')
            line = self.raw.strip()
            try:
                reg = {
                    'PRIVMSG': r'^\:(.*?)\!(.*?)\@(.*\s?) PRIVMSG (.*\s?) \:(.*?)$',
                    'NOTICE': r'^\:(.*?) NOTICE (.*\s?) \:(.*?)$',
                    'KICK': r'^\:(.*?)\!(.*?)\@(.*\s?) KICK (.*\s?) (.*\s?) \:(.*?)$',
                    'MODE': r'^\:(.*?)\!(.*?)\@(.*\s?) MODE (.*?)$'
                }
                # :Liam!uid7517@id-7517.ealing.irccloud.com NICK :[]
                # :[]!uid7517@id-7517.ealing.irccloud.com NICK :Liam

                if line.startswith(':'):
                    if line[1::].split()[0] == self.nick:
                        pass
                    code = line.split()[1]
                    #if code in ['NICK'] or code.isdigit():
                    #    print line
                    if code in ['250', '251', '255']:
                        msg, sender = line.split(':',2)[2], line.split(':',2)[1].split()[0]
                        output.normal('(%s) %s' % (sender, msg), 'NOTICE')
                    if code == 'NICK':
                        nick = line[1::].split('!',1)[0]
                        new_nick = line[1::].split(':',1)[1]
                        output.normal('%s is now known as %s' % (nick, new_nick), 'NICK')
                    if code == 'PRIVMSG':
                        nick, ident, host, sender, msg = re.compile(reg['PRIVMSG']).match(line).groups()
                        msg = self.stripcolors(msg)
                        if msg.startswith('\x01'):
                            msg = '(me) ' + msg.split(' ',1)[1].strip('\x01')
                        output.normal('(%s) %s' % (nick, msg), sender)
                        
                        # self.chan specific
                        if sender.startswith('#'):
                            if not nick in self.chan[sender]:
                                self.chan[sender][nick] = default
                    if code == 'NOTICE':
                        nick, sender, msg = re.compile(reg['NOTICE']).match(line).groups()
                        output.normal('(%s) %s' % (nick.split('!')[0], msg), 'NOTICE')
                    if code == 'KICK':
                        nick, ident, host, sender, kicked, reason = re.compile(reg['KICK']).match(line).groups()
                        output.normal('%s has kicked %s from %s. Reason: %s' % (nick, kicked, sender, reason), 'KICK', 'red')
                    if code == 'MODE':
                        try:
                            nick, ident, host, args = re.compile(reg['MODE']).match(line).groups()
                        except:
                            return
                        output.normal('%s sets MODE %s' % (nick, args), 'MODE')

                    # start gathering info for every channel here
                    # make sure to put after normal line parsing because some functions
                    # will return

                    # 1. Methods:
                    #      - code.chan - dict() keys of channels
                    #      - code.chan['#L'] - get user list
                    #      - code.chan['#L']['Liam'] - get user data
                    #      - code.chan['#L']['Liam']['op'] - get admin
                    default = {'normal': True, 'voiced': False, 'op': False}

                    # :nova.esper.net 353 Test @ #Liam :Test asdlasdkal Testing123 @Liam
                    # :aperture.esper.net 353 Test = #L :Test _123DMWM +vps-2
                    if code == '353':
                        channel, user_list = line[1::].split(':',1)
                        channel, user_list = '#' + channel.split('#',1)[1].strip(), user_list.strip().split()
                        if not channel in self.chan:
                            self.chan[channel] = {}
                        for user in user_list:
                            if user.startswith('@'):
                                name, normal, voiced, op = user[1::], True, True, True
                            elif user.startswith('+'):
                                name, normal, voiced, op = user[1::], True, True, False
                            else:
                                name, normal, voiced, op = user, True, False, False
                            self.chan[channel][name] = {'normal': normal, 'voiced': voiced, 'op': op}
                    
                    if code == 'MODE':
                        # :Liam!liam@liam.ml MODE #Liam +o Code-testing
                        # :Liam!liam@liam.ml MODE #Liam +vv-vv Testing123 Test webuser605 webuser738
                        data = line.split('MODE',1)[1]
                        if len(data.split()) >= 3:
                            channel, modes, users = data.strip().split(' ',2)
                            users = users.split()
                            # :Liam!liam@liam.ml MODE #Liam +vv-vv Testing123 Test webuser605 webuser738
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
                            # From above, we now have a LIST of user dicts()
                            # {'mode': 'v', 'name': 'voiced1', 'sign': '+'}
                            for user in tmp:
                                if user['mode'] in names and user['sign'] in names:
                                    mode, name, sign = names[user['mode']], user['name'], names[user['sign']]
                                    self.chan[channel][name][mode] = sign
                                    if mode == 'op' and sign:
                                        self.chan[channel][name]['voiced'] = True

                    if code == 'JOIN':
                        name = line[1::].split('!',1)[0]
                        channel = line.split('JOIN',1)[1].strip()
                        if name != self.nick:
                            self.chan[channel][name] = default
                    
                    if code == 'PART':
                        name = line[1::].split('!',1)[0]
                        channel = line.split('PART',1)[1].split()[0]
                        del self.chan[channel][name]

                    if code == 'QUIT':
                        # :Liam!liam@liam.ml KICK #LIam webuser :Uhm
                        # :R2D2Warrior!~R2D2@ip70-160-210-75.hr.hr.cox.net QUIT :Msg here
                        name = line[1::].split('!',1)[0]
                        for channel in self.chan:
                            if name in channel:
                                del self.chan[channel][name]

                    # :Liam!liam@liam.ml KICK #L Test :Test
                    if code == 'KICK':
                        tmp = line.split('#',1)[1].split()
                        channel, name = '#' + tmp[0], tmp[1]
                        del self.chan[channel][name]
            except:
                pass

    def stripcolors(self, data):
        """STRIP ALL ZE COLORS! Note: the replacement method is CRUCIAL to keep from
           left over color digits. Order is very important."""
        colors = [u"\x0300", u"\x0301", u"\x0302", u"\x0303", u"\x0304", u"\x0305",
                  u"\x032", u"\x033", u"\x034", u"\x035", u"\x0306", u"\x0307", u"\x0308",
                  u"\x0309", u"\x0310", u"\x0311", u"\x036", u"\x037", u"\x038", u"\x039",
                  u"\x0312", u"\x0313", u"\x0314", u"\x0315", u"\x030", u"\x031", u"\x03",
                  u"\x02", u"\x09", u"\x13", u"\x0f", u"\x15"]
        
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

    def msg(self, recipient, text, log=False, x=False):
        self.sending.acquire()
        text = self.format(text)

        if isinstance(text, unicode):
            try: text = text.encode('utf-8')
            except UnicodeEncodeError, e:
                text = e.__class__ + ': ' + str(e)
        if isinstance(recipient, unicode):
            try: recipient = recipient.encode('utf-8')
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
        if log:
            wait(self.stack_log, text)
        else:
            wait(self.stack, text)

        # Loop detection
        if not log:
            messages = [m[1] for m in self.stack[-8:]]
            if messages.count(text) >= 5:
                text = '...'
                if messages.count('...') > 2:
                    self.sending.release()
                    return

        self.__write(('PRIVMSG', self.safe(recipient)), self.safe(text))
        if log:
            self.stack_log.append((time.time(), text))
        else:
            self.stack.append((time.time(), text))
        self.stack = self.stack[-10:]
        self.stack_log = self.stack_log[-10:]

        self.sending.release()

    def notice(self, dest, text):
        '''Send an IRC NOTICE to a user or a channel. See IRC protocol
           documentation for more information'''
        self.write(('NOTICE', dest), text)

    def action(self, dest, text):
        self.write(('PRIVMSG', dest), '\x01ACTION ' + text + '\x01')

    def error(self, origin):
        try:
            #import traceback
            trace = traceback.format_exc()
            output.error(trace)
            lines = list(reversed(trace.splitlines()))
            report = [lines[0].strip()]
            for line in lines:
                line = line.strip()
                if line.startswith('File "/'):
                    report.append(line[0].lower() + line[1:])
                    break
            else: report.append('{red}Source unknown.')

            self.msg(origin.sender, report[0] + ' (' + report[1] + ')')
        except: self.msg(origin.sender, '{red}Got an error.')

class TestBot(Bot):
    def f_ping(self, origin, match, args):
        delay = match.group(1)
        if delay is not None:
            #import time
            time.sleep(int(delay))
            self.msg(origin.sender, 'pong (%s)' % delay)
        else: self.msg(origin.sender, 'pong')
    f_ping.rule = r'^\.ping(?:[ \t]+(\d+))?$'

def main():
    # bot = TestBot('TestBot', ['#L'])
    # bot.run('irc.esper.net')
    print __doc__

if __name__ == "__main__":
    main()