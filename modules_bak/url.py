#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
url.py - Code Url Module
http://code.liamstanley.io/
"""

import json
import re
from modules import unicode as uc
import urllib2

# this variable is to determine when to use bitly. If the URL is more
# than this length, it'll display a bitly URL instead. To disable bit.ly,
# put None even if it's set to None, triggering .bitly command will still work!
url_re = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
notitle_len = 15
title_len = 70
ignored = [
          'git.io',
          'youtube.',
          'youtu.be',
          'soundcloud.com',
          'imdb.com'
          ]

# Remember, don't use below. Just check ot see if prefix is used..
BLOCKED_MODULES = ['title', 'bitly', 'isup', 'py','youtube','soundcloud']


def get_url_data(url):
    try:
        uri = urllib2.urlopen(url)
        headers = uri.info().headers
        if not uri.info().maintype == 'text':
            return False
        data = uri.read()
        title = re.compile('<title>(.*?)</title>', re.IGNORECASE|re.DOTALL).search(data).group(1)
        return title
    except:
        return False


def get_title_auto(code, input):
    if input.startswith('.'):
        return
    urls = re.findall('(?iu)' + url_re, input)
    tmp = []
    for url in urls:
        test = get_url_data(url)
        if test:
            tmp.append(test)
    code.say(', '.join(tmp))
get_title_auto.rule = ('(?iu).*%s.*' % url_re)
get_title_auto.priority = 'high'

if __name__ == '__main__':
    print __doc__.strip()