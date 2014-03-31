#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
twitter.py - Code Twitter Module
http://code.liamstanley.io/
"""

import re
import urllib2, urllib
from util import web
from util.hook import *

# Input checking...
r_username = re.compile(r'^@?[a-zA-Z0-9_]{1,15}$')
r_hash = re.compile(r'^#[a-zA-Z0-9_]{1,15}$')
r_fullname = re.compile(r'<strong class="fullname">(.*?)</strong>')
r_username = re.compile(r'<span class="username">.*?<span>@</span>(.*?)</span>')
r_time = re.compile(r'<td class="timestamp">.*?</td>')
r_tweet = re.compile(r'<tr class="tweet-container">.*?</tr>')
r_url = re.compile(r'<a href=".*?" class="twitter_external_link.*?" data-url="(.*?)" dir=".*?" rel=".*?" target=".*?">(.*?)</a>')

uri_user = 'https://mobile.twitter.com/%s/'
uri_hash = 'https://mobile.twitter.com/search?q=%s&s=typd'

def get_tweets(url):
    try:
        data = urllib2.urlopen(url).read().replace('\r','').replace('\n','')
        data = re.compile(r'<table class="tweet.*?>.*?</table>').findall(data)
    except:
        return
    tweets = []

    for tweet in data:
        try:
            tmp = {}
            tmp['full'] = r_fullname.findall(tweet)[0].strip()
            tmp['user'] = r_username.findall(tweet)[0].strip()
            tmp['time'] = web.htmlescape(r_time.findall(tweet)[0]).strip()
            tweet_data = t_tweet.findall(tweet)[0].strip()
            urls = r_url.findall(tweet_data)
            for url in urls:
                url = list(url)
                tweet_data = tweet_data.replace(url[1], url[0])
            tmp['text'] = web.htmlescape(tweet_data).strip()
            tweets.append(tmp)
        except:
            continue
    if tweets:
        return tweets
    else:
        return False


def format(tweet, username):
    return '{b}{teal}%s{c} ({purple}@%s{c}){b}' % (tweet, username)


@hook(cmds=['tw','twitter'],ex='twitter liamraystanley', args=True)
def twitter(code, input):
    """twitter <hashtag|username> - Return twitter results for search"""
    err = '{red}{b}Unabled to find any tweets with that search!'
    if r_hash.match(input.group(2)):
        data = get_tweets(uri_hash % urllib.quote(input.group(2)))
        if not data: return code.say(err)
        code.say(format(data[0]['text'], data[0]['user']))
    elif r_username.match(input.group(2)):
        data = get_tweets(uri_user % input.group(2))
        if not data: return code.say(err)
        code.say(format(data[0]['text'], data[0]['user']))