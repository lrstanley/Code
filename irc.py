#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
irc.py - Code A Utility IRC Bot
http://code.liamstanley.net/
"""

import sys, re, time, traceback
import socket, asyncore, asynchat
import os, codecs

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
    try: os.mkdir(cwd + "/logs")
    except Exception, e:
        print >> sys.stderr, 'There was a problem creating the logs directory.'
        print >> sys.stderr, e.__class__, str(e)
        print >> sys.stderr, 'Please fix this and then run code again.'
        sys.exit(1)

def check_logdir():
    if not os.path.isdir(cwd + "/logs"):
        create_logdir()

def log_raw(line):
    check_logdir()
    f = codecs.open(cwd + "/logs/raw.log", 'a', encoding='utf-8')
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
    f.write("\n")
    f.close()

class Bot(asynchat.async_chat):
    def __init__(self, nick, name, channels, password=None, logchan_pm=None, logging=False):
        asynchat.async_chat.__init__(self)
        self.set_terminator('\n')
        self.buffer = ''

        self.nick = nick
        self.user = nick
        self.name = name
        self.password = password

        self.verbose = True
        self.channels = channels or list()
        self.stack = list()
        self.stack_log = list()
        self.logchan_pm = logchan_pm
        self.logging = logging

        import threading
        self.sending = threading.RLock()

    # def push(self, *args, **kargs):
    #     asynchat.async_chat.push(self, *args, **kargs)

    # text styling support
    #Bold            = \x02
    #Color           = \x03
    #Reset           = \x0f
    #Underline       = \x1f
    #Italicized      = \x16

    # coloring method is a bit shabby.
    def findcolor(self, color):
        color = str(color)
        color = color.lower()
        try:
            if color == 'white':
                colorcode = '00'
            elif color == 'black' or color == 'blank' or color == 'clear' or color == 'transparent':
                colorcode = '01'
            elif color == 'blue' or color == 'navy':
                colorcode = '02'
            elif color == 'green':
                colorcode = '03'
            elif color == 'red':
                colorcode = '04'
            elif color == 'brown' or color == 'maroon':
                colorcode = '05'
            elif color == 'purple':
                colorcode = '06'
            elif color == 'orange' or color == 'olive' or color == 'gold':
                colorcode = '07'
            elif color == 'yellow':
                colorcode = '08' #quite a fucking
            elif color == 'lightgreen' or color == 'lime':
                colorcode = '09' #odd bug. wtf mate.
            elif color == 'teal':
                colorcode = '10'
            elif color == 'cyan':
                colorcode = '11'
            elif color == 'lightblue' or color == 'royal':
                colorcode = '12'
            elif color == 'lightpurple' or color == 'pink' or color == 'fuchsia':
                colorcode = '13'
            elif color == 'grey':
                colorcode = '14'
            elif color == 'lightgrey' or color == 'silver':
                colorcode = '01'
            elif color == 'blue' or color == 'navy':
                colorcode = '02'
            elif color == 'green':
                colorcode = '03'
            elif color == 'red':
                colorcode = '04'
            elif color == 'brown' or color == 'maroon':
                colorcode = '05'
            elif color == 'purple':
                colorcode = '06'
            elif color == 'orange' or color == 'olive' or color == 'gold':
                colorcode = '07'
            elif color == 'yellow':
                colorcode = '08' #quite a fucking
            elif color == 'lightgreen' or color == 'lime':
                colorcode = '09' #odd bug. wtf mate.
            elif color == 'teal':
                colorcode = '10'
            elif color == 'cyan':
                colorcode = '11'
            elif color == 'lightblue' or color == 'royal':
                colorcode = '12'
            elif color == 'lightpurple' or color == 'pink' or color == 'fuchsia':
                colorcode = '13'
            elif color == 'grey':
                colorcode = '14'
            elif color == 'lightgrey' or color == 'silver':
                colorcode = '15'
            return str(colorcode)
        except:
            colorcode = ''
            return str(colorcode)

    def color(self, color, message):
        try:
            if self.config.textstyles:
                try:
                    color = str(color)
                    message = str(message)
                    color = color.split('/') #split, if two different colors
                    message = '\x03' + self.findcolor(color[0]) + ',' + self.findcolor(color[1]) + message + '\x03'
                except: #fail, which means only one color specified
                    message = '\x03' + self.findcolor(color[0]) + message + '\x03'
            else:
                pass
            return message
        except:
            return message

    def bold(self, message):
        try:
            if self.config.textstyles:
                message = str(message)
                message = '\x02' + message + '\x02'
            else:
                pass
            return message
        except:
            return message
			
    def italic(self, message):
        try:
            if self.config.textstyles:
                message = str(message)
                message = '\x16' + message + '\x16'
            else:
                pass
            return message
        except:
            return message

    def underline(self, message):
        try:
            if self.config.textstyles:
                 message = str(message)
                 message = '\x1f' + message + '\x1f'
            else:
                pass
            return message
        except:
            return message

    def __write(self, args, text=None, raw=False):
        # print '%r %r %r' % (self, args, text)
        try:
            if raw:
                temp = ' '.join(args)[:510] + " :" + text + '\r\n'
                self.push(temp)
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
            #the fuck went wrong m8.
            #print "INDEXERROR", text
            #pass

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
            input = input.replace('\n', '')
            input = input.replace('\r', '')
            if u:
                input = input.encode('utf-8')
        return input

    def run(self, host, port=6667):
        self.initiate_connect(host, port)

    def initiate_connect(self, host, port):
        if self.verbose:
            message = 'Connecting to %s:%s...' % (host, port)
            print >> sys.stderr, message,
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
        try: asyncore.loop()
        except KeyboardInterrupt:
            sys.exit()

    def handle_connect(self):
        if self.verbose:
            print >> sys.stderr, 'connected!'
        if self.password:
            self.write(('PASS', self.password))
        self.write(('NICK', self.nick))
        self.write(('USER', self.user, '+iw', self.nick), self.name)

    def changenick(self, nick):
        chars = set('`+=;,<>?')
        if not any((c in chars) for c in nick) and nick[0] != '-' and \
        len(nick) =< 1 and len(nick) =< 16:
            self.write(('NICK', self.nick))
            self.nick = nick
            return True
        else:
            return False

    def handle_close(self):
        self.close()
        print >> sys.stderr, 'Closed!'

    def collect_incoming_data(self, data):
        self.buffer += data
        if data:
            if self.logchan_pm:
                dlist = data.split()
                if len(dlist) >= 3:
                    if "#" not in dlist[2] and dlist[1].strip() not in IRC_CODES:
                        self.msg(self.logchan_pm, data, True)
            if self.logging:
                log_raw(data)

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
        self.write(('NOTICE', dest), text)

    def error(self, origin):
        try:
            #import traceback
            trace = traceback.format_exc()
            print trace
            lines = list(reversed(trace.splitlines()))

            report = [lines[0].strip()]
            for line in lines:
                line = line.strip()
                if line.startswith('File "/'):
                    report.append(line[0].lower() + line[1:])
                    break
            else: report.append('source unknown')

            self.msg(origin.sender, report[0] + ' (' + report[1] + ')')
        except: self.msg(origin.sender, "Got an error.")

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
