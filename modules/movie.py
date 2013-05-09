# -*- coding: utf8 -*-
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
movie.py - Code movie Module
http://code.liamstanley.net/

Module imported from jenni.
"""

import web
import urllib2


def movie(code, input):
    """.imdb movie/show title -- displays information about a production"""

    if not input.group(2):
        return
    word = input.group(2).rstrip()
    word = word.replace(" ", "+")
    uri = "http://www.imdbapi.com/?t=" + word

    uri = uri.encode('utf-8')
    page = web.get(uri)
    data = web.json(page)

    if data['Response'] == 'False':
        if 'Error' in data:
            message = '[MOVIE] %s' % data['Error']
        else:
            code.debug('movie',
                        'Got an error from the imdb api,\
                                search phrase was %s' %
                        word, 'warning')
            code.debug('movie', str(data), 'warning')
            message = '[MOVIE] Got an error from imdbapi'
    else:
        message = code.color('blue', code.bold('[MOVIE] Title: ') + data['Title'] + \
                   code.color('blue', code.bold(' | Year: ')) + data['Year'] + \
                  code.color('blue', code.bold(' | Rating: ')) + data['imdbRating'] + \
                  code.color('blue', code.bold(' | Genre: ')) + data['Genre'] + \
                  code.color('blue', code.bold(' | IMDB Link: ')) + 'http://imdb.com/title/' + data['imdbID']
    code.say(message)
movie.commands = ['movie', 'imdb']
movie.example = '.movie Movie Title'

if __name__ == '__main__':
    print __doc__.strip()
