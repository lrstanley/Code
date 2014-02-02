#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
youtube.py - Code Youtube Module
http://code.liamstanley.io/
"""

import json
import urllib2
import time

api_url = 'http://gdata.youtube.com/feeds/api/videos/%s?v=2&alt=jsonc'
search_url = 'http://gdata.youtube.com/feeds/api/videos?max-results=1&v=2&alt=jsonc&start-index=%s&q=%s'

def youtube(code, input):
    """Automatically find the information from a youtube url and display it
       to users in a channel"""
    try:
        if '//www.youtube.com/watch?v=' in input.group().lower():
            id = input.group().split('/watch?v=',1)[1]
        elif '//youtu.be/' in input.group().lower():
            id = input.group().split('youtu.be/',1)[1]
        if '&' in id: id = id.split('&',1)[0]
        if ' ' in id: id = id.split()[0]
        data = json.loads(urllib2.urlopen(api_url % id).read())['data']
        
        # Set some variables, because we'll have to modify a vew before we spit them back out!
        reply = create_response(data,url=False)
        return code.say(' - '.join(reply))
    except:
        return
youtube.rule = r'.*'
youtube.priority = 'medium'
youtube.thread = False

def get_search(code, input):
    """Search youtube for the top video of <query>. Also note, you can specify next response with a number at the end"""
    if not input.group(2): return code.reply('Invalid syntax: \'.yt <search query>\'')
    if input.group(2).strip().split()[-1].isdigit():
        numerical = int(input.group(2).strip().split()[-1])
        if numerical < 1: return code.reply('Invalid search number: \'.yt <search query> <#>\'')
    else: numerical = 1   
    try:
        query = input.group(2).replace(' ','+')
        data = json.loads(urllib2.urlopen(search_url % (str(numerical),query)).read())['data']
        reply = create_response(data['items'][0],url=True)
        return code.say(' - '.join(reply))
    except:
        return code.reply(code.color('red','Failed to search for %s!' % input.group(2)))
get_search.rate = 10
get_search.commands = ['youtube','yt','video']
get_search.example = '.yt PewDiePie 7'

def create_response(data,url=False):
    reply = []
    # Should surely have a title, but just in case :P
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
    # Number of views. Yuck.
    if 'viewCount' in data:
        reply.append('\x0313\x02%s\x0f\x02 views' % format(data['viewCount'], ',d'))
    upload_time = parse_date(data['uploaded'])
    reply.append('by \x0313\x02%s\x0f\x02 on \x0313\x02%s\x0f\x02' % (data['uploader'],upload_time))
    # Dis shit not be child appr0ved
    if 'contentRating' in data:
        reply.append('\x0304NSFW\x02')
    if url and data['player']['default']:
       reply.append(data['player']['default'].split('&',1)[0].strip())
    return reply

def parse_date(thedate):
    upload_time = time.strptime(thedate, '%Y-%m-%dT%H:%M:%S.000Z')
    return time.strftime("%Y.%m.%d", upload_time)

if __name__ == '__main__':
    print __doc__.strip()
