#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
search.py - Code Web Search Module
http://code.liamstanley.io/
"""


import re
import web
from modules.url import shorten
from tools import *

class Grab(web.urllib.URLopener):
    def __init__(self, *args):
        self.version = 'Mozilla/5.0 (code)'
        web.urllib.URLopener.__init__(self, *args)
        self.addheader('Referer', 'https://github.com/Liamraystanley/Code')
    def http_error_default(self, url, fp, errcode, errmsg, headers):
        return web.urllib.addinfourl(fp, [headers, errcode], "http:" + url)

def google_ajax(query):
    """Search using AjaxSearch, and return its JSON."""
    if isinstance(query, unicode):
        query = query.encode('utf-8')
    uri = 'https://ajax.googleapis.com/ajax/services/search/web'
    args = '?v=1.0&safe=off&q=' + web.urllib.quote(query)
    handler = web.urllib._urlopener
    web.urllib._urlopener = Grab()
    bytes = web.get(uri + args)
    web.urllib._urlopener = handler
    return web.json(bytes)

def google_search(query):
    results = google_ajax(query)
    try: return results['responseData']['results'][0]['unescapedUrl']
    except IndexError: return None
    except TypeError:
        print results
        return False

def google_count(query):
    results = google_ajax(query)
    if not results.has_key('responseData'): return '0'
    if not results['responseData'].has_key('cursor'): return '0'
    if not results['responseData']['cursor'].has_key('estimatedResultCount'):
        return '0'
    return results['responseData']['cursor']['estimatedResultCount']

def formatnumber(n):
    """Format a number with beautiful commas."""
    parts = list(str(n))
    for i in range((len(parts) - 3), 0, -3):
        parts.insert(i, ',')
    return ''.join(parts)

def g(code, input):
    """Queries Google for the specified input."""
    if empty(code, input): return
    query = input.group(2)
    query = query.encode('utf-8')
    uri = google_search(query)
    if uri:
        code.reply(shorten(uri))
        if not hasattr(code.bot, 'last_seen_uri'):
            code.bot.last_seen_uri = {}
        code.bot.last_seen_uri[input.sender] = uri
    elif uri is False: code.reply("Problem getting data from Google.")
    else: code.reply("No results found for '%s'." % code.color('purple',query))
g.commands = ['g', 'search', 'google']
g.priority = 'high'
g.example = 'g swhack'
g.rate = 30

def gc(code, input):
    """Returns the number of Google results for the specified input."""
    if empty(code, input): return
    query = input.group(2)
    query = query.encode('utf-8')
    num = formatnumber(google_count(query))
    code.say(query + ': ' + num)
gc.commands = ['gc']
gc.priority = 'high'
gc.example = 'gc extrapolate'
gc.rate = 30

r_query = re.compile(
    r'\+?"[^"\\]*(?:\\.[^"\\]*)*"|\[[^]\\]*(?:\\.[^]\\]*)*\]|\S+'
)

def gcs(code, input):
    if empty(code, input): return
    queries = r_query.findall(input.group(2))
    if len(queries) > 6:
        return code.reply('Sorry, can only compare up to six things.')

    results = []
    for i, query in enumerate(queries):
        query = query.strip('[]')
        query = query.encode('utf-8')
        n = int((formatnumber(google_count(query)) or '0').replace(',', ''))
        results.append((n, query))
        if i >= 2: __import__('time').sleep(0.25)
        if i >= 4: __import__('time').sleep(0.25)

    results = [(term, n) for (n, term) in reversed(sorted(results))]
    reply = ', '.join('%s (%s)' % (t, formatnumber(n)) for (t, n) in results)
    code.say(reply)
gcs.commands = ['gcs', 'comp']
gcs.rate = 30

r_bing = re.compile(r'<h3><a href="([^"]+)"')

def bing_search(query, lang='en-GB'):
    query = web.urllib.quote(query)
    base = 'http://www.bing.com/search?mkt=%s&q=' % lang
    bytes = web.get(base + query)
    m = r_bing.search(bytes)
    if m: return m.group(1)

def bing(code, input):
    """Queries Bing for the specified input."""
    if empty(code, input): return
    query = input.group(2)
    lang = 'en-GB'
    query = query.encode('utf-8')
    uri = bing_search(query, lang)
    if uri:
        code.reply(uri)
        if not hasattr(code.bot, 'last_seen_uri'):
            code.bot.last_seen_uri = {}
        code.bot.last_seen_uri[input.sender] = uri
    else: code.reply("No results found for '%s'." % code.bold(query))
bing.commands = ['bing']
bing.example = 'bing swhack'
bing.rate = 30

r_duck = re.compile(r'nofollow" class="[^"]+" href="(.*?)">')

#def duck_search(query):
#    query = query.replace('!', '')
#    query = web.urllib.quote(query)
#    uri = 'https://duckduckgo.com/html/?q=%s&kl=us-en&kp=-1' % query
#    bytes = web.get(uri)
#    m = r_duck.search(bytes)
#    if m: return web.decode(m.group(1))

#def duck(code, input):
#    query = input.group(2)
#    if not query: return code.reply('.search what?')
#    query = query.encode('utf-8')
#    uri = duck_search(query)
#    if uri:
#        code.reply(uri)
#        if not hasattr(code.bot, 'last_seen_uri'):
#            code.bot.last_seen_uri = {}
#        code.bot.last_seen_uri[input.sender] = uri
#    else: code.reply("No results found for '%s'." % code.bold(query))
#duck.commands = ['duck', 'ddg'] #google function below is broken, this will suffice for now :/
#duck.rate = 30

#def search(code, input):
#    if not input.group(2):
#        return code.reply('.search for what?')
#    query = input.group(2).encode('utf-8')
#    gu = google_search(query) or '-'
#    bu = bing_search(query) or '-'
#    du = duck_search(query) or '-'

#    if (gu == bu) and (bu == du):
#        result = '%s %s' % (gu, code.bold(code.color('blue', '(Google, Bing, Duck)')))
#    elif (gu == bu):
#        result = '%s %s, %s %s' % (gu, code.bold(code.color('blue', '(Google, Bing)')), du, code.bold(code.color('blue', '(Duck)')))
#    elif (bu == du):
#        result = '%s %s, %s %s' % (bu, code.bold(code.color('blue', '(Bing, Duck)')), gu, code.bold(code.color('blue', '(Google)')))
#    elif (gu == du):
#        result = '%s %s, %s %s' % (gu, code.bold(code.color('blue', '(Google, Duck)')), bu, code.bold(code.color('blue', '(Bing)')))
#    else:
#        if len(gu) > 250: gu = code.bold('(extremely long link)')
#        if len(bu) > 150: bu = code.bold('(extremely long link)')
#        if len(du) > 150: du = code.bold('(extremely long link)')
#        result = '%s %s, %s %s, %s %s' % (gu, code.bold(code.color('blue', '(Google)')), bu, code.bold(code.color('blue', '(Bing)')), du, code.bold(code.color('blue', '(Duck)')))

#    code.reply(result)
#search.commands = ['all']
#search.rate = 30

def suggest(code, input):
    if empty(code, input): return
    query = input.group(2).encode('utf-8')
    uri = 'http://websitedev.de/temp-bin/suggest.pl?q='
    answer = web.get(uri + web.urllib.quote(query).replace('+', '%2B'))
    if answer:
        if answer.find('No suggestions for ') > -1:
            answer = code.color('red', 'Sorry, no result.')
            code.reply(answer)
        else:
            code.reply(answer)
    else: code.reply(code.color('red', 'Sorry, no result.'))
suggest.commands = ['suggest', 'sugg']
suggest.example = 'suggest apples'
suggest.rate = 30

if __name__ == '__main__':
    print __doc__.strip()