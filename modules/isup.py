from urllib import urlopen
from util.hook import *


@hook(cmds=['isup', 'isdown', 'check', 'up', 'down'], ex='isup http://google.com', args=True)
def isup(code, input):
    """isup <url> - Is it down for everyone, or just you?"""
    try:
        data = urlopen('http://isup.me/%s' % input.group(2)).read()
        if 'not just you' in data:
            return code.say('{red}%s is down! It\'s not just you!' % input.group(2))
        elif 'It\'s just you.' in data:
            return code.say('{green}%s is up! Must just be you!' % input.group(2))
        else:
            return code.say('{red}Failed to get the status of the website!')
    except:
        return code.say('{red}Failed to get the status of the website!')
