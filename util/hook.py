def deprecated(old):
    def new(code, input, old=old):
        self = code
        origin = type('Origin', (object,), {
            'sender': input.sender,
            'nick': input.nick
        })()
        match = input.match
        args = [input.bytes, input.sender, '@@']

        old(self, origin, match, args)
    new.__module__ = old.__module__
    new.__name__ = old.__name__
    return new


def empty(code, input, response=None):
    if not response:
        response = 'No arguments supplied! Try: "{b}{purple}%shelp <command>{b}{r}"' % code.prefix
    if not input.group(2):
        code.say(response)
        return True
    else:
        return False


def error(code):
    code.say('Incorrect usage! Try: "{b}{purple}%shelp <command>{b}{r}"' %
             code.prefix)


def admin(code, input):
    if input.owner:
        return True
    code.say('{b}{red}You are not authorized to use that command!')


def notauthed(code):
    response = '{b}{red}You are not authorized to use that command!'
    code.say(response)


def owner(code, input):
    if input.owner:
        return True
    code.say('{b}{red}You are not authorized to use that command!')

# /SOME/ of these ones are decorators customized to respond from call()
#    in bot.py and defaults in bind_commands() (mainly admin/owner)


def hook(
    commands=None, command=None, cmds=None, cmd=None, example=None, ex=None,
    rate=None, rule=None, priority=None, thread=None, event=None, args=None,
        admin=None, owner=None, voiced=None, op=None):
    def add_attribute(func):
        # This is kinda ugly looking, but it does quite the job.
        if commands is not None:
            func.commands = list(commands)
        if command is not None:
            func.commands = list(command)
        if cmds is not None:
            func.commands = list(cmds)
        if cmd is not None:
            func.commands = list(cmd)
        if example is not None:
            func.example = str(example)
        if ex is not None:
            func.example = str(ex)
        if rate is not None:
            func.rate = int(rate)
        if rule is not None:
            func.rule = str(rule)
        if priority is not None:
            func.priority = str(priority)
        if thread is not None:
            func.thread = bool(thread)
        if event is not None:
            func.event = str(event).upper()
        if args is not None:
            func.args = bool(args)
        if admin is not None:
            func.admin = bool(admin)
        if owner is not None:
            func.owner = bool(owner)
        # Custom to user tracking...
        if voiced is not None:
            func.voiced = bool(voiced)
        if op is not None:
            func.op = bool(op)
        # if op != None:
        #    pass
        return func
    return add_attribute
