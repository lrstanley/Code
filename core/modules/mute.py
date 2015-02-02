from util.hook import *


@hook(cmds=['mute'], trusted=True, thread=False)
def mute(code, input):
    """ mute - Mutes the bot. Only usable by admins, owners, and ops. """
    code.mute()
    return code.action('is now muted.')


@hook(cmds=['unmute'], trusted=True, thread=False)
def unmute(code, input):
    """ unmute - Unmutes the bot. Only usable by admins, owners, and ops. """
    code.unmute()
    return code.action('is now unmuted.')
