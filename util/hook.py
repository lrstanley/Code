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

custom = [
    'admin', 'args', 'owner', 'op', 'trusted', 'voiced', 'supress',
    'ischannel', 'selfopped'
]

hooks = {
    'commands': {'origin': 'commands'},
    'cmds': {'origin': 'commands'},
    'example': {'origin': 'example'},
    'ex': {'origin': 'example'},
    'rate': {'origin': 'rate'},
    'rule': {'origin': 'rule'},
    'priority': {'origin': 'priority'},
    'thread': {'origin': 'thread'},
    'threaded': {'origin': 'thread'},
    'event': {'origin': 'event'}
}


def hook(**kwargs):
    def add_attribute(func):
        for key, value in kwargs.items():
            if key not in hooks:
                setattr(func, key, value)
            else:
                setattr(func, hooks[key]['origin'], value)

        for key in custom:
            if key in kwargs:
                setattr(func, key, kwargs[key])
            else:
                setattr(func, key, False)
        return func
    return add_attribute
