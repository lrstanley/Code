#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
search.py - Code Search Module
http://code.liamstanley.io/
"""

import re
from json import loads as json
from urllib import quote
import urllib2
import util.web
from util.hook import *
import HTMLParser
h = HTMLParser.HTMLParser()

uri = 'https://ajax.googleapis.com/ajax/services/search/web?v=1.0&safe=off&q=%s'

def google_search(query):
    """Search using Googles AjaxSearch functionality."""
    try:
        data = util.web.get(uri % quote(query)).read()
    except:
        return False
    if not data:
        return False
    return json(data)


@hook(cmds['search','google','g'], ex='search Twitter API', rate=10, args=True)
def search(code, input):
    """Queries Google for the specified input."""
    r = google_search(input.group(2))
    if uri is False:
        return code.reply("Problem getting data from Google.")
    if not r['responseData']['results']:
        return code.reply("No results found for '{purple}%s{c}'." % input.group(2))
    urls = r['responseData']['results']
    if len(urls) > 3:
        urls = urls[0:3]

    count, time = r['responseData']['cursor']['resultCount'], r['responseData']['cursor']['searchResultTime'] + 's'
    # Make the count prettified
    count_commas = [m.start() for m in re.finditer(r'{}'.format(re.escape(',')), count)]
    if len(count_commas) == 1:
        count = count.split(',',1)[0] + 'k'
    elif len(count_commas) == 2:
        count = count.split(',',1)[0] + 'm'
    elif len(count_commas) == 3:
        count = count.split(',',1)[0] + 'b'
    output = []
    r_type = code.format('{b}{title}{b}{c} - {link}')
    colors, color_count = ['{blue}', '{teal}', '{green}'], 0
    for url in urls:
        # Change colors based on priority
        color = colors[color_count]
        color_count += 1
        # Remove html formatting
        title = h.unescape(re.sub(r'\<.*?\>', '', url['title']).strip())
        # Restrict sizing of titles to no longer than 50 chars
        if len(title) > 50:
            title = title[0:44] + '[...]'
        # Shorten URL to fit more responses cleaner
        link = url['url']
        if hasattr(code.config, 'shortenurls'):
            if code.config.shortenurls:
                link = util.web.shorten(url['url'])
        output.append(color + r_type.format(title=title, link=link))
    code.say('%s ({b}%s{b}, {b}%s{b} results)' % (' | '.join(output), time, count))


@hook(cmds=['gc'], priority='high', ex='gc extrapolate', rate=10, args=True)
def gc(code, input):
    """Returns the number of Google results for the specified input."""
    r = google_search(input.group(2))
    if uri is False:
        return code.reply("Problem getting data from Google.")
    if not r['responseData']['results']:
        return code.reply("No results found for '{purple}%s{c}'." % input.group(2))
    urls = r['responseData']['results']
    return code.say('%s: {b}%s{b} results found.' % (input.group(2), r['responseData']['cursor']['resultCount']))
    code.say(query + ': ' + num)