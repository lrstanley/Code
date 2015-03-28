import re
import threading
import time
from util import output
from core.wrapper import input_wrapper, wrapped, check_perm


def decode(bytes):
    try:
        text = bytes.decode('utf-8')
    except UnicodeDecodeError:
        try:
            text = bytes.decode('iso-8859-1')
        except UnicodeDecodeError:
            text = bytes.decode('cp1252')
    return text


def dispatch(self, origin, args):
    bytes, event, args = args[0], args[1], args[2:]
    text = decode(bytes)

    # Check permissions specifically for the blocking, so we're
    # not blocking admins/owners.
    admin = check_perm(origin, [self.config('owner')])
    if not admin:
        admin = check_perm(origin, self.config('admins', []))

    # Blocking here...
    match = [True if re.match(mask, '{}!{}@{}'.format(origin.nick, origin.user, origin.host)) else False for mask in self.re_blocks]
    if True in match and not admin:
        output.warning('Ignoring user %s matching a mask in the ignore list' % (origin.nick), 'BLOCKS')
        return

    for priority in ('high', 'medium', 'low'):
        items = self.commands[priority].items()
        for regexp, funcs in items:
            for func in funcs:
                if event != func.event:
                    continue

                match = regexp.match(text)
                if not match:
                    continue

                code = wrapped(self, origin, text, match)
                input = input_wrapper(code, origin, text, bytes, match, event, args)

                if func.thread:
                    targs = (self, func, origin, code, input)
                    t = threading.Thread(target=call, args=targs)
                    t.start()
                else:
                    call(self, func, origin, code, input)


def call(self, func, origin, code, input):
    input.channel = input.sender if input.sender.startswith('#') else False
    # custom decorators
    if func.ischannel and not input.channel:
        if not func.supress:
            code.say('{b}That can only be used in a channel!')
        return

    try:
        if func.op and not code.chan[input.sender][input.nick]['op']:
            if not func.supress:
                code.say('{b}{red}You must be op to use that command!')
            return

        if func.voiced and not code.chan[input.sender][input.nick]['voiced']:
            if not func.supress:
                code.say('{b}{red}You must be voiced to use that command!')
            return

        input.op = code.chan[input.sender][input.nick]['op']
        input.voiced = code.chan[input.sender][input.nick]['voiced']
        input.chan = code.chan[input.sender]
    except KeyError:
        pass

    if func.admin and not input.admin or func.trusted and not input.trusted:
        if not func.supress:
            code.say('{b}{red}You are not authorized to use that command!')
        return

    if func.owner and not input.owner:
        if not func.supress:
            code.say('{b}{red}You must be owner to use that command!')
        return

    if func.args and not input.group(2):
        msg = '{red}No arguments supplied! Try: ' + \
              '"{b}{purple}%shelp %s{b}{r}"'
        return code.say(msg % (code.prefix, code.doc[func.name]['commands'][0]))

    if func.selfopped and not code.chan[input.sender][code.nick]['op']:
        return code.say('{b}{red}I do not have op. I cannot execute this command.')

    nick = input.nick.lower()
    if nick in self.times:
        # per-command rate limiting
        if func in self.times[nick]:
            if not input.admin:
                if time.time() - self.times[nick][func] < func.rate:
                    self.times[nick][func] = time.time()
                    return
    else:
        self.times[nick] = dict()
    self.times[nick][func] = time.time()
    try:
        if self.excludes:
            if input.sender in self.excludes:
                if '!' in self.excludes[input.sender]:
                    # block all function calls for this channel
                    return
                fname = func.func_code.co_filename.split('/')[-1].split('.')[0]
                if fname in self.excludes[input.sender]:
                    # block function call if channel is blacklisted
                    return output.error('Blocks', 'Blocked: %s from %s' % (input.sender, func.name))
    except:
        output.error("Error attempting to block: ", str(func.name))
        self.error(origin)

    try:
        func_return = func(code, input)
        if isinstance(func_return, str) or isinstance(func_return, unicode):
            code.say(func_return)
    except:
        if not func.supress:
            self.error(origin)
        else:
            self.error(origin, supress=True)
