import re
from util import web
from util.hook import *


def getdata(user):
    try:
        data = web.get('http://ws.audioscrobbler.com/1.0/user/%s/recenttracks.rss' % (user))
        print data.encoding
    except:
        return False
    if 'No user exists with this name.' in data.text:
        return False
    return data


@hook(cmds=['lastfm', 'lfm'], ex='lastfm liamraystanley', args=True, rate=10)
def lastfm(code, input):
    """ lfm <username> -- Pull last played song for the user """
    user = input.group(2).split()[0].strip().lower()
    data = getdata(user)
    data = data.text.encode('ascii', 'ignore')
    if not data:
        return code.say('Username {} does not exist in the last.fm database.'.format(user))
    song = web.striptags(re.compile(r'<title>.*?</title>').findall(data)[1])
    code.reply('{purple}' + web.escape(song).replace('  ', ' -- ', 1) + '{c} {red}(via Last.Fm)')
