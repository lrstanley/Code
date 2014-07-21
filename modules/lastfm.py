import re
from util import web
from util.hook import *

# This is the default user to check for last fm
defaultuser = 'liamraystanley'


def getdata(user):
    try:
        data = web.get(
            'http://ws.audioscrobbler.com/1.0/user/%s/recenttracks.rss' % (user)).read()
    except:
        return False
    if 'No user exists with this name.' in data:
        return False
    else:
        return data


@hook(cmds=['lastfm', 'lfm'], ex='lastfm liamraystanley', rate=10)
def lastfm(code, input):
    # just .lfm
    if defaultuser and not input.group(2):
        user = defaultuser
        data = getdata(user)
        if not data:
            return code.say('Username %s does not exist in the last.fm database.' % (user))
        else:
            song = re.compile(r'<title>.*?</title>').findall(data)[1]
            song = re.sub(r'\<.*?\>', '', song).strip()
            code.reply('{purple}%s{c} {red}(via Last.Fm)' % song)
    # .lfm <username>
    elif input.group(2):
        user = input.group(2).split()[0].strip().lower()
        data = getdata(user)
        if not data:
            return code.say('Username %s does not exist in the last.fm database.' % (user))
        else:
            song = re.compile(r'<title>.*?</title>').findall(data)[1]
            song = re.sub(r'\<.*?\>', '', song).strip()
            code.reply('{purple}%s{c} {red}(via Last.Fm)' % song)
