import re
from util import web
from util.hook import *


api_key = 'c4b768d9b2f82b4a478e602e66ac718c'
api_uri = 'http://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&user={user}&limit=1&format=json&api_key={key}'


@hook(cmds=['lastfm', 'lfm'], ex='lastfm liamraystanley', args=True, rate=5)
def lastfm(code, input):
    """ lfm <username> -- Pull last played song for the user """
    user = input.group(2).split()[0].strip()
    data = web.json(api_uri.format(user=user, key=api_key))['recenttracks']
    if len(data['track']) == 0:
        return code.say('Username {} does not exist in the last.fm database.'.format(user))

    track = data['track'][0]
    artist, song, url = track['artist']['#text'], track['name'], track['url']
    code.reply(code.format('{purple}{song} -- {artist}{c} {url}').format(artist=artist, song=song, url=url))

