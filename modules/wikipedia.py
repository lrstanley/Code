#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
wikipedia.py - Code Wikipedia Module
http://code.liamstanley.io/
"""

from urllib import quote as urlify
from urllib2 import urlopen as get
from json import loads as jsonify
from util.hook import *

lang = 'en'
maxlen = '220'

wikipedia_url = 'wikipedia.org'
wikiquote_url = 'wikiquote.org'

full_define = 'https://%s.%s/w/api.php?action=query&prop=extracts&explaintext&exsectionformat=plain&exchars=%s&titles=%s&format=json'
full_search = 'https://%s.%s/w/api.php?action=opensearch&search=%s&format=json'


def wikiSearch(query, url, results=5):
    """Use MediaWikis API to search for values from wiktionary and wikipedia"""
    # First, we need to grab the data, and serialize it in JSON
    url_query = urlify(query)
    data = jsonify(get(full_search % (lang, url, url_query)).read())

    # Check to see if we have #(results as arg form) results, then make a list
    if not data[1]:
        return False
    if len(data[1]) > results:
        return data[1][:results]
    else:
        # Assume it's smaller than or = 5
        return data[1]


def wikiDefine(term, url):
    """Use MediaWikis API to define a value from wiktionary and wikipedia"""
    # First, we need to grab the data, and serialize it in JSON
    url_query = urlify(term)
    data = jsonify(get(full_define % (lang, url, maxlen, url_query)).read())['query']['pages']

    # We need to see if it was found. If it wasn't it'll be a -1 page
    for pageNumber, pageData in data.iteritems():
        if pageNumber == '-1':
            # Assume failed to find
            return False
        else:
            # Assume found a result. Now, find and return the title/contents.
            if pageData['extract'].startswith('REDIRECT'):
                return False  # This means it's a redirect page according to MediaWiki API
            title = pageData['title']
            content = pageData['extract'].encode('ascii', 'ignore').replace('\n', ' ')
            while '  ' in content:
                content = content.replace('  ', ' ')
            return [title, content]


@hook(cmds=['wiki', 'w'], ex='wiki speaker', args=True)
def wikipedia(code, input):
    """Pull definitions/search from wikipedia.org"""
    try:
        # Try to get the definition of what they WANT
        data = wikiDefine(input.group(2).strip(), wikipedia_url)  # 1:title, 2:content
        if not data:
            # Assume it's working, just no definition..
            # Try and give them search results
            search = wikiSearch(input.group(2).strip(), wikipedia_url)  # list() of results
            if not search:
                # Crap. No results for this either?
                return code.say('No Wiki page for %s! (Try \'.wsearch\')' % input.group(2).strip())
            else:
                # Make nice sexy results, because we're sorry we couldn't find it...
                return code.say('Unable to find results. Try: {purple}%s{c}' % ', '.join(search))
        else:
            # Working, print out a nice clean definition.
            print repr(data[1])
            return code.say('{purple}%s{c}: %s' % (data[0], data[1]))
    except:
        return code.say('Failed to get the definition!')


@hook(cmds=['wdefine', 'wsearch', 'wikisearch', 'swiki'], ex='wsearch yellow', args=True)
def wikipediaSearch(code, input):
    """Pull search results from wikipedia.org"""
    try:
        search = wikiSearch(input.group(2).strip(), wikipedia_url)  # list() of results
        if not search:
            # Crap. No results for this either?
            return code.say('No Wiki page for {purple}%s{c}!' % input.group(2).strip())
        else:
            # Make nice sexy results, because we're sorry we couldn't find it...
            return code.say('Suggestions: {purple}%s{c}' % ', '.join(search))
    except:
        return code.say('{red}No suggestions found!')
