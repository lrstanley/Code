from util.hook import *


@hook(cmds=['mute'], admin=True)
def mute(code, input):
    code.set('muted', True)
    return code.say('{b}%s is now muted.' % code.nick)


@hook(cmds=['unmute'], admin=True)
def unmute(code, input):
    code.set('muted', False)
    return code.say('{b}%s is now unmuted.' % code.nick)
