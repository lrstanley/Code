#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
soundcloud.py - Code Soundcloud Module
http://code.liamstanley.io/
"""

import json
import urllib2
from util.hook import *

client = '97c32b1cc8e9875be21f502bde81aaeb'
uri = 'http://api.soundcloud.com/resolve.json?url=http://soundcloud.com/%s&client_id=%s'
sc_regex = r'https?://soundcloud.com\/'


@hook(rule=sc_regex)
def soundcloud(code, input):
    """Automatically find the information from a soundcloud url and display it
       to users in a channel"""
    try:
        id = input.group().split('soundcloud.com/', 1)[1].split()[0].strip()
        # Should look like 'artist/song'
        data = json.loads(urllib2.urlopen(uri % (id, client)).read())
        output = []
        # Get date first so we can add to the title
        year, month, day = data['created_at'].split()[0].split('/')
        # Should always have a title
        output.append('\x0313\x02%s\x02\x03 (\x0313\x02%s/%s/%s\x02\x03)' % (data['title'], month, day, year))
        # Should always have an artist
        output.append('uploaded by \x0313\x02%s\x02\x03' % data['user']['username'])
        # Genre!
        output.append('\x0313\x02' + data['genre'] + '\x02\x03')
        # Playback count, if none, obviously don't add it
        if int(data['playback_count']) > 0:
            output.append('\x0313\x02%s\x02\x03 plays' % data['playback_count'])
        # Download count, if none, obviously don't add it
        if int(data['download_count']) > 0:
            output.append('\x0313\x02%s\x02\x03 downloads' % data['download_count'])
        # And the same thing with the favorites count
        if int(data['favoritings_count']) > 0:
            output.append('\x0313\x02%s\x02\x03 favs' % data['favoritings_count'])
        # Comments too!
        if int(data['comment_count']) > 0:
            output.append('\x0313\x02%s\x02\x03 comments' % data['comment_count'])
        # Tags!
        if len(data['tag_list'].split()) > 0:
            tmp = data['tag_list'].split()
            tags = []
            for tag in tmp:
                tags.append('(#\x0313\x02%s\x02\x03)' % tag)
            output.append(' '.join(tags))
        return code.say(' - '.join(output))
    except:
        return


def convert_time(seconds):  # data[17]
    length = seconds
    lenout = ''
    # if length / 86400: # > 1 day
    #    lenout += '%dd ' % (length / 86400)
    if length / 3600:  # > 1 hour
        lenout += '%dh ' % (length / 3600)
    if length / 60:  # > Minutes
        lenout += '%dm ' % (length / 60 % 60)
        lenout += "%ds" % (length % 60)
    return lenout
