#!/usr/bin/env python
"""
Stan-Derp Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
search.py - Stan-Derp Web Search Module
http://standerp.liamstanley.net/
"""


import re
import web

class Grab(web.urllib.URLopener):
    def __init__(self, *args):
        self.version = 'Mozilla/5.0 (standerp)'
        web.urllib.URLopener.__init__(self, *args)
        self.addheader('Referer', 'https://github.com/myano/standerp')
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

def g(standerp, input):
    """Queries Google for the specified input."""
    query = input.group(2)
    if not query:
        return standerp.reply('.g what?')
    query = query.encode('utf-8')
    uri = google_search(query)
    if uri:
        standerp.reply(uri)
        if not hasattr(standerp.bot, 'last_seen_uri'):
            standerp.bot.last_seen_uri = {}
        standerp.bot.last_seen_uri[input.sender] = uri
    elif uri is False: standerp.reply("Problem getting data from Google.")
    else: standerp.reply("No results found for '%s'." % query)
g.commands = ['g']
g.priority = 'high'
g.example = '.g swhack'
g.rate = 30

def gc(standerp, input):
    """Returns the number of Google results for the specified input."""
    query = input.group(2)
    if not query:
        return standerp.reply('.gc what?')
    query = query.encode('utf-8')
    num = formatnumber(google_count(query))
    standerp.say(query + ': ' + num)
gc.commands = ['gc']
gc.priority = 'high'
gc.example = '.gc extrapolate'
gc.rate = 30

r_query = re.compile(
    r'\+?"[^"\\]*(?:\\.[^"\\]*)*"|\[[^]\\]*(?:\\.[^]\\]*)*\]|\S+'
)

def gcs(standerp, input):
    if not input.group(2):
        return standerp.reply("Nothing to compare.")
    queries = r_query.findall(input.group(2))
    if len(queries) > 6:
        return standerp.reply('Sorry, can only compare up to six things.')

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
    standerp.say(reply)
gcs.commands = ['gcs', 'comp']
gcs.rate = 30

r_bing = re.compile(r'<h3><a href="([^"]+)"')

def bing_search(query, lang='en-GB'):
    query = web.urllib.quote(query)
    base = 'http://www.bing.com/search?mkt=%s&q=' % lang
    bytes = web.get(base + query)
    m = r_bing.search(bytes)
    if m: return m.group(1)

def bing(standerp, input):
    """Queries Bing for the specified input."""
    query = input.group(2)
    if query.startswith(':'):
        lang, query = query.split(' ', 1)
        lang = lang[1:]
    else: lang = 'en-GB'
    if not query:
        return standerp.reply('.bing what?')

    query = query.encode('utf-8')
    uri = bing_search(query, lang)
    if uri:
        standerp.reply(uri)
        if not hasattr(standerp.bot, 'last_seen_uri'):
            standerp.bot.last_seen_uri = {}
        standerp.bot.last_seen_uri[input.sender] = uri
    else: standerp.reply("No results found for '%s'." % query)
bing.commands = ['bing']
bing.example = '.bing swhack'
bing.rate = 30

r_duck = re.compile(r'nofollow" class="[^"]+" href="(.*?)">')

def duck_search(query):
    query = query.replace('!', '')
    query = web.urllib.quote(query)
    uri = 'https://duckduckgo.com/html/?q=%s&kl=us-en&kp=-1' % query
    bytes = web.get(uri)
    m = r_duck.search(bytes)
    if m: return web.decode(m.group(1))

def duck(standerp, input):
    query = input.group(2)
    if not query: return standerp.reply('.ddg what?')

    query = query.encode('utf-8')
    uri = duck_search(query)
    if uri:
        standerp.reply(uri)
        if not hasattr(standerp.bot, 'last_seen_uri'):
            standerp.bot.last_seen_uri = {}
        standerp.bot.last_seen_uri[input.sender] = uri
    else: standerp.reply("No results found for '%s'." % query)
duck.commands = ['search','duck', 'ddg']
duck.rate = 30

def search(standerp, input):
    if not input.group(2):
        return standerp.reply('.search for what?')
    query = input.group(2).encode('utf-8')
    gu = google_search(query) or '-'
    bu = bing_search(query) or '-'
    du = duck_search(query) or '-'

    if (gu == bu) and (bu == du):
        result = '%s (g, b, d)' % gu
    elif (gu == bu):
        result = '%s (g, b), %s (d)' % (gu, du)
    elif (bu == du):
        result = '%s (b, d), %s (g)' % (bu, gu)
    elif (gu == du):
        result = '%s (g, d), %s (b)' % (gu, bu)
    else:
        if len(gu) > 250: gu = '(extremely long link)'
        if len(bu) > 150: bu = '(extremely long link)'
        if len(du) > 150: du = '(extremely long link)'
        result = '%s (g), %s (b), %s (d)' % (gu, bu, du)

    standerp.reply(result)
search.commands = ['google']
search.rate = 30

def suggest(standerp, input):
    if not input.group(2):
        return standerp.reply("No query term.")
    query = input.group(2).encode('utf-8')
    uri = 'http://websitedev.de/temp-bin/suggest.pl?q='
    answer = web.get(uri + web.urllib.quote(query).replace('+', '%2B'))
    if answer:
        standerp.say(answer)
    else: standerp.reply('Sorry, no result.')
suggest.commands = ['suggest']
suggest.rate = 30

if __name__ == '__main__':
    print __doc__.strip()
