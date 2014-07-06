from util.hook import *


@hook(cmds=['mute'], admin=True, thread=False)
def mute(code, input):
    code.mute()
    return code.say('{b}%s is now muted.' % code.nick)


@hook(cmds=['unmute'], admin=True, thread=False)
def unmute(code, input):
    code.unmute()
    return code.say('{b}%s is now unmuted.' % code.nick)
