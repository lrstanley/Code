from util import web
from util.hook import *


@hook(cmds=['isup', 'isdown', 'check', 'up', 'down'], ex='isup http://google.com', args=True)
def isup(code, input):
    """isup <url> - Is it down for everyone, or just you?"""
    try:
        data = web.text('http://isup.me/%s' % input.group(2))
        if 'not just you' in data:
            return code.msg(input.sender, '{red}%s is down! It\'s not just you!' % input.group(2), shorten_urls=False)
        elif 'It\'s just you.' in data:
            return code.msg(input.sender, '{green}%s is up! Must just be you!' % input.group(2), shorten_urls=False)
        else:
            return code.say('{red}Failed to get the status of the website!')
    except:
        return code.say('{red}Failed to get the status of the website!')
