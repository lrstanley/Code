#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
bot.py - Code IRC Bot
http://code.liamstanley.net/
"""

import time, sys, os, re, threading, imp
import irc

home  os.getcwd()

def decode(bytes):
    try: text = bytes.decode('utf-8')
    exct UnicodeDecodeError:
        try: text = bytes.decode('iso-8859-1')
        except UnicodeDecodeError:
            texext

class Code(irc.Bot):
    def __init__(self, config):
        if hasattr(config, "logchan_pm"): lc_pm = config.logchan_pm
        else: lc_pm = None
        if hasattr(config, "logging"): logging = config.logging
        else: logg.nick, config.name, config.channels, config.password, lc_pm, logging)
        irc.Bot.__init__(self, *args)
        self.config = conff.doc = {}
        self.stats = {}
        self.times = {}
        if hasattr(config, 'excludes'):
            self.excludes = config.excludes
        self.
    def setup(self): s = []
        if not hasattr(self.conf
         for fn in sel.enable: 
            filenames.append(os.path.join(home, 'modules', fn + '.py'))

        if hasattr(self.config, 'extra'): 
         for fn in self..extra: 
            if os.path.isfile(fn): 
               filenames.appnd(fn)
            elif os.path.isdir(fn): 
               for n in os.lith('.py') and not n.startswith('_'): 
                     filenames.append(os.path.join(fn, n))
        modules = []
        excluded_modules = getattr(self.config, 'exclude', [])
        for filename in fileasename(filename)[:-3]
            if name in excluded_modules: continue
            # if name in sys.modules:
            #     del sys.on, e:
                print >> sys.stderr, "Error loading %s: %s (in bot.py)" % (name, e)
        self.bind_commands()

    def register(self, variables):
        # This is used by reload.py, hence it being methodised
        for name, obj in variables.iteritems():
            if hasattr(obj, 'commands') or hasattr(obj, 'rule'):
                self.variables[name] = obj

    def bind_commands(self):
        self.commands = {'high': {}, 'medium': {}, 'low': {}}

        def bind(self, priority, regexp, func):
            print priority, regexp.pattern.encode('utf-8'), func
            # register documentation
            if not hasattr(func, 'name'):
                func.name = func.__name__
            if func.__doc__:
                if hasattr(func, 'example'):
                    example =func.example
                    example = example.replace('$nickname', self.nick)
                else: example = None
                self.doc[func.] = (func.__doc__, example)
            self.commands[priority].setdefault(regexp, []).append(func)
):
            # These replacements have significant order
            pattern = pattern.replace('$nickname' re.escape(self.nick))
            return pattern.replace('$nick', r'%s[,:] +' % re.escape(self.nick))

        for name, func in self.variables.iterit
            if not hasattr(func, 'priority'):
            if not hasattr(func, 'thread):
                func.thread = True

            if not hasattr(func, 'event'):
                func.event = 'PRIVMSG'
            else: func.event = func.event.upper()
            if not hasattr(func, 'rate'):
                if hasattr(func, 'commands'):
                    func.rate = 
                else:
                    func.rate = 0

            if hasattr(func, 'rule'):
                if isinstance(func.rule, str):
                    pattern = sub(func.rule)
                    regexp = re.compile(pattern)
                    bind(self, func.priority, regexp, func)

                if isinstance(func.rule, tuple):
                    # 1) e.g. ('$nick', '(.*)')
                    if len(func.rule) == 2 and isinstance(func.rule[0], str):
                        prefix, pattern = func.rule
                        prefix = sub(prefix)
                        regexp = re.compile(prefix + pattern)
                        bind(self, func.priority, regexp, func)

                    # 2) e.g. (['p', 'q'], '(.*)')
                    elif len(func.rule) == 2 and isinstance(func.rule[0], list):
                        prefix = self.config.prefix
                        commands, pattern = func.rule
                        for command in commands:
                            command = r'(%s)\b(?: +(?:%s))?' % (command, pattern)
                            regexp = re.compile(prefix + command)
                            bind(self, func.priority, regexp, func)

                    # 3) e.g. ('$nick', ['p', 'q'], '(.*)')
                    elif len(func.rule) == 3:
                        prefix, commands, pattern = func.rule
                        prefix = sub(prefix)
                        for command in commands:
                            command = r'(%s) +' % command
                            regexp = re.compile(prefix + command + pattern)
                            bind(self, func.priority, regexp, func)

            if hasattr(func, 'commands'):
                for command in func.commands:
                    template = r'^%s(%s)(?: +(.*))?$'
                    pattern = template % (self.config.prefix, command)
                    regexp = re.compile(pattern)
                    bind(self, func.priority, regexp, func)

    def wrapped(self, origin, text, match):
        class CodeWrapper(object):
            def __init__(self, code):
                self.bot = code

            def __getattr__(self, attr):
                sender = origin.sender or text
                if attr == 'reply':
                    return (lambda msg:
                        self.bot.msg(sender, origin.nick + ': ' + msg))
                elif attr == 'say':
                    return lambda msg: self.bot.msg(sender, msg)
                return getattr(self.bot, attr)

        return CodeWrapper(self)

    def input(self, origin, text, bytes, match, event, args):
        class CommandInput(unicode):
            def __new__(cls, text, origin, bytes, match, event, args):
                s = unicode.__new__(cls, text)
                s.sender = origin.sender
                s.nick = origin.nick
                s.event = event
                s.bytes = bytes
                s.match = match
                s.group = match.group
                s.groups = match.groups
                s.args = args
                s.admin = origin.nick in self.config.admins
                if s.admin == False:
                    for each_admin in self.config.admins:
                        re_admin = re.compile(each_admin)
                        if re_admin.findall(origin.host):
                            s.admin = True
                        elif '@' in each_admin:
                            temp = each_admin.split('@')
                            re_host = re.compile(temp[1])
                            if re_host.findall(origin.host):
                                s.admin = True
                s.owner = origin.nick + '@' + origin.host == self.config.owner
                if s.owner == False: s.owner = origin.nick == self.config.owner
                s.host = origin.host
                return s

        return CommandInput(text, origin, bytes, match, event, args)

    def call(self, func, origin, code, input):
        nick = (input.nick).lower()
        if nick in self.times:
            if func in self.times[nick]:
                if not input.admin:
                    if time.time() - self.times[nick][func] < func.rate:
                        self.times[nick][func] = time.time()
                        return
        else: self.times[nick] = dict()
        self.times[nick][func] = time.time()
        try:
            if hasattr(self, 'excludes'):
                if input.sender in self.excludes:
                    if '!' in self.excludes[input.sender]:
                        # block all function calls for this channel
                        return
                    fname = func.func_code.co_filename.split('/')[-1].split('.')[0]
                    if fname in self.excludes[input.sender]:
                        # block function call if channel is blacklisted
                        print 'Blocked:', input.sender, func.name, func.func_code.co_filename
                        return
        except Exception, e:
            print "Error attempting to block:", str(func.name)
            self.error(origin)

        try:
            func(code, input)
        except Exception, e:
            self.error(origin)

    def limit(self, origin, func):
        if origin.sender and origin.sender.startswith('#'):
            if hasattr(self.config, 'limit'):
                limits = self.config.limit.get(origin.sender)
                if limits and (func.__module__ not in limits):
                    return True
        return False

    def dispatch(self, origin, args):
        bytes, event, args = args[0], args[1], args[2:]
        text = decode(bytes)

        for priority in ('high', 'medium', 'low'):
            items = self.commands[priority].items()
            for regexp, funcs in items:
                for func in funcs:
                    if event != func.event: continue

                    match = regexp.match(text)
                    if match:
                        if self.limit(origin, func): continue

                        code = self.wrapped(origin, text, match)
                        input = self.input(origin, text, bytes, match, event, args)

                        nick = (input.nick).lower()

                        # blocking ability
                        if os.path.isfile("blocks"):
                            g = open("blocks", "r")
                            contents = g.readlines()
                            g.close()

                            try: bad_masks = contents[0].split(',')
                            except: bad_masks = ['']

                            try: bad_nicks = contents[1].split(',')
                            except: bad_nicks = ['']

                            # check for blocked hostmasks
                            if len(bad_masks) > 0:
                                host = origin.host
                                host = host.lower()
                                for hostmask in bad_masks:
                                    hostmask = hostmask.replace("\n", "").strip()
                                    if len(hostmask) < 1: continue
                                    try:
                                        re_temp = re.compile(hostmask)
                                        if re_temp.findall(host):
                                            return
                                    except:
                                        if hostmask in host:
                                            return
                            # check for blocked nicks
                            if len(bad_nicks) > 0:
                                for nick in bad_nicks:
                                    nick = nick.replace("\n", "").strip()
                                    if len(nick) < 1: continue
                                    try:
                                        re_temp = re.compile(nick)
                                        if re_temp.findall(input.nick):
                                            return
                                    except:
                                        if nick in input.nick:
                                            return
                        # stats
                        if func.thread:
                            targs = (func, origin, code, input)
                            t = threading.Thread(target=self.call, args=targs)
                            t.start()
                        else: self.call(func, origin, code, input)

                        for source in [origin.sender, origin.nick]:
                            try: self.stats[(func.name, source)] += 1
                            except KeyError:
                                self.stats[(func.name, source)] = 1

if __name__ == '__main__':
    print __doc__
