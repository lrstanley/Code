from util.hook import *


@hook(cmds=['mute'], admin=True, thread=False)
def mute(code, input):
    code.mute()
    return code.action('is now muted.')


@hook(cmds=['unmute'], admin=True, thread=False)
def unmute(code, input):
    code.unmute()
    return code.action('is now unmuted.')
