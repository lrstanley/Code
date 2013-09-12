#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
youtube.py - Code Youtube Module
http://code.liamstanley.net/
"""

import json
import urllib2
import time

api_url = 'http://gdata.youtube.com/feeds/api/videos/%s?v=2&alt=jsonc'

def youtube(code, input):
    """Automatically find the information from a youtube url and display it
       to users in a channel"""
    reply = []
    #if not '//www.youtube.com/watch?v=' in input.group().lower(): return
    try:
        if '//www.youtube.com/watch?v=' in input.group().lower():
            id = input.group().split('/watch?v=',1)[1]
        elif '//youtu.be/' in input.group().lower():
            id = input.group().split('youtu.be/',1)[1]
        if '&' in id: id.split('&',1)[0]
        if ' ' in id: id = id.split()[0]
        data = json.loads(urllib2.urlopen(api_url % id).read())['data']
        
        # set some variables, because we'll have to modify a vew before we spit them back out!
        
        # should surely have a title, but just in case :P
        if 'title' in data:
            reply.append('\x0313\x02' + data['title'] + '\x0f\x02')
        # Some length data ;)
        if 'duration' in data:
            length = data['duration']
            lenout = ''
            if length / 3600:  # > 1 hour
                lenout += '%dh ' % (length / 3600)
            if length / 60:
                lenout += '%dm ' % (length / 60 % 60)
                lenout += "%ds" % (length % 60)
            reply.append('length \x0313\x02%s\x0f\x02' % lenout)
        # Shitty video? FIND OUT!
        if 'rating' in data and 'ratingCount' in data:
            reply.append('rated \x0313\x02%.2f/5.0\x0f\x02 (\x0313\x02%d\x0f\x02)' % (data['rating'],
                                                      data['ratingCount']))
        # NUmber of views
        if 'viewCount' in data:
            reply.append('\x0313\x02%s\x0f\x02 views' % format(data['viewCount'], ',d'))
        upload_time = time.strptime(data['uploaded'], '%Y-%m-%dT%H:%M:%S.000Z')
        reply.append('by \x0313\x02%s\x0f\x02 on \x0313\x02%s\x0f\x02' % (data['uploader'],time.strftime("%Y.%m.%d", upload_time)))
        # Dis shit not be child appr0ved
        if 'contentRating' in data:
            reply.append('\x0304NSFW\x02')
        return code.say(' - '.join(reply))
    except:
        return
youtube.rule = r'.*'
youtube.priority = 'medium'
youtube.thread = False


if __name__ == '__main__':
    print __doc__.strip()
