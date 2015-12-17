import re
from util import web
from util import database
from util.hook import *


api_key = 'c4b768d9b2f82b4a478e602e66ac718c'
api_uri = 'http://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&user={user}&limit=1&format=json&api_key={key}'


@hook(cmds=['lastfm', 'lfm'], ex='lastfm liamraystanley', args=False, rate=5)
def lastfm(code, input):
    """ lfm <username> -- Pull last played song for the user """

    db = database.get(code.nick, 'lastfm')
    if not db:
        db = {}

    if input.group(2):
        user = input.group(2).split()[0].strip()
    else:
        if input.nick not in db:
            return code.say('{b}{red}No arguments supplied! Try: "%shelp lastfm"' % code.prefix)

        user = db[input.nick]

    data = web.json(api_uri.format(user=user, key=api_key))['recenttracks']
    if len(data['track']) == 0:
        return code.say('Username {} does not exist in the last.fm database.'.format(user))

    db[input.nick] = user
    database.set(code.nick, db, 'lastfm')

    track = data['track'][0]
    artist, song, url, name = track['artist']['#text'], track['name'], track['url'], data['@attr']['user']
    code.reply(code.format('{purple}{song} -- {artist}{c} - {pink}{user}{c} - {url}').format(artist=artist, song=song, url=url, user=name))

