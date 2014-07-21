#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
bot.py - Code IRC Bot
https://www.liamstanley.io/Code.git
"""


import sys
sys.path += ['lib']
import time
import os
import re
import threading
import imp
from core import irc
from core.call import call
from core.bind import bind_commands
from util import output

home = os.getcwd()


def decode(bytes):
    try:
        text = bytes.decode('utf-8')
    except UnicodeDecodeError:
        try:
            text = bytes.decode('iso-8859-1')
        except UnicodeDecodeError:
            text = bytes.decode('cp1252')
    return text


class Code(irc.Bot):

    def __init__(self, raw_config):
        self.load = []
        self.unload = []
        self.raw_config = raw_config
        debug = self.config('debug', False)
        args = (
            raw_config['nick'], raw_config['name'], raw_config['user'],
            raw_config['channels'], raw_config['server_password'], debug
        )
        irc.Bot.__init__(self, *args)
        self.prefix = self.config('prefix', '.')
        self.doc = {}
        self.times = {}
        self.modules = []
        self.cmds = {}
        self.data = {}
        self.bot_startup = int(time.time())
        self.excludes = self.config('excluded_per_channel', [])
        self.setup()

    def config(self, key=None, default=None):
        if not key:
            return self.raw_config
        if key in self.raw_config:
            return self.raw_config[key]
        else:
            if default:
                return default
            return False

    def setup(self):
        self.variables = {}

        filenames, core_filenames = [], []
        for fn in os.listdir(os.path.join(home, 'modules')):
            if fn.endswith('.py') and not fn.startswith('_'):
                if self.config('whitelisted_modules', False):
                    if fn.split('.', 1)[0] not in self.config('whitelisted_modules', []):
                        continue
                filenames.append(os.path.join(home, 'modules', fn))

        if self.config('extra'):
            for fn in self.config('extra'):
                if os.path.isfile(fn):
                    filenames.append(fn)
                elif os.path.isdir(fn):
                    for n in os.listdir(fn):
                        if n.endswith('.py') and not n.startswith('_'):
                            filenames.append(os.path.join(fn, n))

        # Add system modules that the user should always require. Still can
        #  be removed by deleting them or moving them out of the system
        #  modules directory
        for fn in os.listdir(os.path.join(home, 'core/modules')):
            if fn.endswith('.py') and not fn.startswith('_'):
                filenames.append(os.path.join(home, 'core/modules', fn))
                core_filenames.append(fn.split('.', 1)[0])

        excluded_modules = self.config('excluded_modules', [])
        if self.load:
            for filename in self.load:
                # Add user specified modules on reload
                if filename in filenames:
                    continue
                try:
                    fn = os.path.join(home, 'modules', filename + '.py')
                    filenames.append(fn)
                except:
                    continue
        filenames = sorted(list(set(filenames)))
        # Reset some variables that way we don't get dups
        self.modules = []
        self.cmds = {}

        # Load modules
        for filename in filenames:
            name = os.path.basename(filename)[:-3]
            if name in excluded_modules and name not in self.load:
                # If the file was excluded via the config file
                # Don't exclude if purposely loaded
                continue
            if name in self.unload:
                # If the module was excluded via the reload module
                continue
            # if name in sys.modules:
            #     del sys.modules[name]
            self.setup_module(name, filename)

        tmp_modules = []
        for module in self.modules:
            if module not in core_filenames:
                tmp_modules.append(module)
        if core_filenames:
            output.info('Loaded {} core modules: {}'.format(
                len(core_filenames), ', '.join(core_filenames)))
        if self.modules:
            output.info('Loaded {} modules: {}'.format(
                len(tmp_modules), ', '.join(tmp_modules)))
        else:
            output.warning('Couldn\'t find any modules')

        bind_commands(self)

    def setup_module(self, name, filename, is_startup=True):
        try:
            module = imp.load_source(name, filename)
            if hasattr(module, 'setup'):
                module.setup(self)
            self.register(vars(module))
            self.modules.append(name)
            self.modules = sorted(list(set(self.modules)))
        except Exception as e:
            output.error("Failed to load %s: %s" % (name, e))
            if not is_startup:
                # Only raise exception again if it's user-triggered
                raise Exception("Failed to load %s: %s" % (name, e))

    def register(self, variables):
        # This is used by reload.py, hence it being methodised
        for name, obj in variables.iteritems():
            if hasattr(obj, 'commands') or hasattr(obj, 'rule'):
                self.variables[name] = obj

    def wrapped(self, origin, text, match):
        class CodeWrapper(object):

            def __init__(self, code):
                self.bot = code

            def __getattr__(self, attr):
                sender = origin.sender or text
                if attr == 'reply':
                    return lambda msg: self.bot.msg(sender, '{}: {}'.format(origin.nick, msg))
                elif attr == 'action':
                    return lambda action: self.bot.me(sender, action)
                elif attr == 'say':
                    return lambda msg: self.bot.msg(sender, msg)
                elif attr == 'action':
                    return lambda msg: self.bot.action(sender, msg)
                return getattr(self.bot, attr)

        return CodeWrapper(self)

    def input(self, origin, text, bytes, match, event, args):
        class CommandInput(unicode):

            def __new__(cls, text, origin, bytes, match, event, args):
                s = unicode.__new__(cls, text)
                s.sender = origin.sender
                s.nick = origin.nick
                s.user = origin.user
                s.host = origin.host
                s.event = event
                s.bytes = bytes
                s.match = match
                s.group = match.group
                s.groups = match.groups
                s.args = args
                if not hasattr(s, 'data'):
                    s.data = {}

                if origin.sender.startswith('#'):
                    try:
                        s.op = self.chan[origin.sender][origin.nick]['op']
                        s.voiced = self.chan[origin.sender][origin.nick]['voiced']
                    except KeyError:
                        s.op, s.voiced = False, False
                else:
                    s.op, s.voiced = False, False

                def check_perm(origin, trigger):
                    """
                        Match and figure out if the user that's triggering it matches
                        the configured admin/owner/whatever
                    """
                    for matching in trigger:
                        if '!' in matching and '@' in matching:
                            # nick!user@host
                            trigger_nick, other = matching.split('!', 1)
                            trigger_user, trigger_host = other.split('@', 1)
                            if trigger_nick.lower() == origin.nick.lower() and \
                               trigger_user.lower() == origin.user.lower() and \
                               trigger_host.lower() == origin.host.lower():
                                return True
                            continue
                        elif '@' in matching and not matching.startswith('@'):
                            # user@host
                            trigger_user, trigger_host = matching.split('@', 1)
                            if trigger_user.lower() == origin.user.lower() and \
                               trigger_host.lower() == origin.host.lower():
                                return True
                            continue
                        elif '@' in matching:
                            # @host
                            trigger_host = matching[1::]
                            if trigger_host.lower() == origin.host.lower():
                                return True
                            continue
                        else:
                            # host OR nick
                            if matching.lower() == origin.nick.lower() or \
                               matching.lower() == origin.host.lower():
                                return True
                            continue
                    return False
                
                s.owner = check_perm(origin, [self.config('owner')])
                if s.owner:
                    s.admin = True
                else:
                    s.admin = check_perm(origin, self.config('admins', []))

                return s

        return CommandInput(text, origin, bytes, match, event, args)

    def dispatch(self, origin, args):
        bytes, event, args = args[0], args[1], args[2:]
        text = decode(bytes)

        for priority in ('high', 'medium', 'low'):
            items = self.commands[priority].items()
            for regexp, funcs in items:
                for func in funcs:
                    if event != func.event:
                        continue

                    match = regexp.match(text)
                    if not match:
                        continue

                    code = self.wrapped(origin, text, match)
                    input = self.input(
                        origin, text, bytes, match, event, args
                    )

                    nick = input.nick.lower()
                    # blocking ability
                    if os.path.isfile("blocks"):
                        g = open("blocks", "r")
                        contents = g.readlines()
                        g.close()

                        try:
                            bad_masks = contents[0].split(',')
                        except:
                            bad_masks = ['']

                        try:
                            bad_nicks = contents[1].split(',')
                        except:
                            bad_nicks = ['']

                        # check for blocked hostmasks
                        if len(bad_masks) > 0:
                            host = origin.host
                            host = host.lower()
                            for hostmask in bad_masks:
                                hostmask = hostmask.replace(
                                    "\n", "").strip()
                                if len(hostmask) < 1:
                                    continue
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
                                if len(nick) < 1:
                                    continue
                                try:
                                    re_temp = re.compile(nick)
                                    if re_temp.findall(input.nick):
                                        return
                                except:
                                    if nick in input.nick:
                                        return

                    if func.thread:
                        targs = (self, func, origin, code, input)
                        t = threading.Thread(target=call, args=targs)
                        t.start()
                    else:
                        call(self, func, origin, code, input)

    def get(self, key):
        if key in self.data:
            return self.data[key]
        else:
            return False

    def set(self, key, data):
        try:
            self.data[key] = data
            return True
        except:
            return False
