import re
from util import web
from util.hook import *


def getdata(user):
    try:
        data = web.get(
            'http://ws.audioscrobbler.com/1.0/user/%s/recenttracks.rss' % (user)).read()
    except:
        return False
    if 'No user exists with this name.' in data:
        return False
    return data


@hook(cmds=['lastfm', 'lfm'], ex='lastfm liamraystanley', args=True, rate=10)
def lastfm(code, input):
    user = input.group(2).split()[0].strip().lower()
    data = getdata(user)
    if not data:
        return code.say('Username %s does not exist in the last.fm database.' % (user))
    song = web.striptags(re.compile(r'<title>.*?</title>').findall(data)[1])
    code.reply('{purple}%s{c} {red}(via Last.Fm)' % web.htmlescape(song))
