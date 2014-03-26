#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
url.py - Code Url Module
http://code.liamstanley.io/
"""

import json
import re
from urllib import quote
from urllib2 import urlopen
from HTMLParser import HTMLParser
from util.web import shorten
h = HTMLParser()

url_re = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
notitle_len = 4
title_len = 80
nourl_len = 15
url_len = 70
ignored = ['git.io', 'youtube.', 'youtu.be', 'soundcloud.com', 'imdb.com','ci.liamstanley.io']


def get_url_data(url):
    if len(url) > url_len or len(url) < nourl_len:
        return False# URL is either really long, or really short. Don't need shortening.
    try:
        uri = urlopen(url)
        headers = uri.info().headers
        if not uri.info().maintype == 'text':
            return False
        data = uri.read(1024) # Only read soo much of a large site.
        title = re.compile('<title>(.*?)</title>', re.IGNORECASE|re.DOTALL).search(data).group(1)
        title = h.unescape(title)
        title = title.replace('\n', '').replace('\r', '')

        # Remove spaces...
        while '  ' in title:
            title = title.replace('  ', ' ')

        # Shorten LONG urls
        if len(title) > 200:
            title = title[:200] + '[...]'

        if len(title) > title_len or len(title) < notitle_len: # Title output too large/short
            return False

        return unicode(title)
    except:
        return False


def clean_url(url):
    head, other = url.split('//',1)
    return head + '//' + other.split('/')[0]


def get_title_auto(code, input):
    if input.startswith(code.prefix): return # Prevent triggering of other plugins
    urls = re.findall('(?iu)' + url_re, input)
    # If a user wants to spam... lets limit is to 3 URLs max, per line
    if len(urls) > 3:
        urls = urls[0:3]
    output = []
    for url in urls:
        # check to see if we should ignore this URL...
        for bad in ignored:
            if bad.lower() in url.lower():
                continue
        # Lets get some data!
        data = get_url_data(url)
        if data:
            if hasattr(code.config, 'shortenurls'):
                if code.config.shortenurls:
                    url = shorten(url)
                else:
                    url = clean_url(url)
            else:
                url = clean_url(url)
            output.append('{blue}{b}%s{b}{c} - %s' % (data, url))
    return code.say(' | '.join(output))
get_title_auto.rule = ('(?iu).*%s.*' % url_re)
get_title_auto.priority = 'high'


if __name__ == '__main__':
    print __doc__.strip()