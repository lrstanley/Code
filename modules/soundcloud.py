#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
soundcloud.py - Code Soundcloud Module
http://code.liamstanley.net/
"""

import json, urllib2

client = '97c32b1cc8e9875be21f502bde81aaeb'
uri = 'http://api.soundcloud.com/resolve.json?url=http://soundcloud.com/%s/%s&client_id=%s'

def soundcloud(code, input):
    """Automatically find the information from a soundcloud url and display it
       to users in a channel"""
    try:
        if not '//soundcloud.com/' in input.group().lower():
            return
        id = input.group().split('soundcloud.com/',1)[1].split()[0].strip()
        # Should look like 'artist/song'
        if '#' in id: id = id.split('#',1)[0]
        artist, song = id.split('/')
        data = json.loads(urllib2.urlopen(uri % (artist,song,client)).read())
        output = []
        # Get date first so we can add to the title
        year, month, day = data['created_at'].split()[0].split('/')
        # Should always have a title
        output.append('%s (%s/%s/%s)' % (data['title'], month, day, year))
        # Should always have an artist
        output.append('uploaded by %s' % data['user']['username'])
        # Genre!
        output.append(data['genre'])
        # Playback count, if none, obviously don't add it
        if int(data['playback_count']) > 0:
            output.append('%s plays' % data['playback_count'])
        # Download count, if none, obviously don't add it
        if int(data['download_count']) > 0:
            output.append('%s downloads' % data['download_count'])
        # And the same thing with the favorites count
        if int(data['favoritings_count']) > 0:
            output.append('%s favs' % data['favoritings_count'])
        # Comments too!
        if int(data['comment_count']) > 0:
            output.append('%s comments' % data['comment_count'])
        # Tags!
        if len(data['tag_list'].split()) > 0:
            tmp = data['tag_list'].split()
            tags = []
            for tag in tmp:
                tags.append('(#%s)' % tag)
            output.append(' '.join(tags))
        return code.say(' - '.join(output))
    except:
        return
soundcloud.rule = r'.*'
soundcloud.priority = 'medium'
soundcloud.thread = False

def convert_time(seconds): # data[17]
    length = seconds
    lenout = ''
    #if length / 86400: # > 1 day
    #    lenout += '%dd ' % (length / 86400)
    if length / 3600:  # > 1 hour
        lenout += '%dh ' % (length / 3600)
    if length / 60: # > Minutes
        lenout += '%dm ' % (length / 60 % 60)
        lenout += "%ds" % (length % 60)
    return lenout

if __name__ == '__main__':
    print __doc__.strip()