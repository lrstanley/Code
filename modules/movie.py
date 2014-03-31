# -*- coding: utf8 -*-
"""
Code Copyright (C) 2012-2014 Liam Stanley
movie.py - Code Movie Module
http://code.liamstanley.io/
"""

import urllib
import urllib2
import json
from util.hook import *

search_uri = 'http://www.omdbapi.com/?t=%s'
id_uri = 'http://www.omdbapi.com/?i=%s'
error = 'Unable to search for that movie!'
movie_regex = r'https?://.*?imdb\.com\/title\/'


@hook(cmds=['movie', 'imdb'], ex='movie Transformers', args=True)
def movie_search(code, input):
    """imdb movie/show title -- displays information about a production"""
    try:
        # Url-ify
        search = urllib.quote(input.group(2).strip())

        # Pull response from API, and load into a JSON based dict()
        data = json.loads(urllib2.urlopen(search_uri % (search)).read())

        # If we get an error from the API. (Other errors are caught from the try:;except:)
        if data['Response'] == 'False':
            return code.reply(error)

        # Start creating a response
        response = build_response(data)
        output = []
        for section in response:
            output.append('{blue}%s{c}: %s' % (section[0], section[1]))
        return code.say(' | '.join(output))
    except:
        return code.reply(error)


@hook(rule=movie_regex)
def movie(code, input):
    """Automatically find the information from a imdb url and display it
       to users in a channel"""
    try:
        id = input.group().split('imdb.com/title/', 1)[1]
        if '/' in id:
            id = id.split('/', 1)[0]
        data = json.loads(urllib2.urlopen(id_uri % id).read())

        # If we get an error from the API. (Other errors are caught from the try:;except:)
        if data['Response'] == 'False':
            return

        # Start creating a response
        response = build_response(data)
        output = []
        for section in response:
            output.append('{blue}%s{c}: %s' % (section[0], section[1]))
        return code.say(' | '.join(output))
    except:
        return

def build_response(data):
    response = list()
    response.append(['Title', data['Title']])
    response.append(['Rated', data['Rated']])
    response.append(['Year', data['Year']])
    response.append(['Rating', data['imdbRating']])
    response.append(['Genre', data['Genre']])
    response.append(['Votes', data['imdbVotes']])
    response.append(['Link', 'http://imdb.com/title/%s/' % (data['imdbID'])])
    return response