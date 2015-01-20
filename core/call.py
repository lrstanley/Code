import time
from util import output


def call(self, func, origin, code, input):
    # custom decorators
    if func.ischannel and not input.sender.startswith('#'):
        return code.say('{b}That can only be used in a channel!')

    try:
        if func.op and not code.chan[input.sender][input.nick]['op']:
            return code.say('{b}{red}You must be op to use that command!')

        if func.voiced and not code.chan[input.sender][input.nick]['voiced']:
            return code.say('{b}{red}You must be voiced to use that command!')

        input.op = code.chan[input.sender][input.nick]['op']
        input.voiced = code.chan[input.sender][input.nick]['voiced']
        input.chan = code.chan[input.sender]
    except KeyError:
        pass

    if func.admin and not input.admin or func.trusted and not input.trusted:
        return code.say('{b}{red}You are not authorized to use that command!')

    if func.owner and not input.owner:
        return code.say('{b}{red}You must be owner to use that command!')

    if func.args and not input.group(2):
        msg = '{red}No arguments supplied! Try: ' + \
              '"{b}{purple}%shelp %s{b}{r}"'
        return code.say(msg % (
            code.prefix,
            code.doc[func.name]['commands'][0])
        )

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
