#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
urban.py - Code Urban Dictionary Module
http://code.liamstanley.net/
"""

from urllib2 import urlopen as get
from urllib import quote as quote
from json import loads as jsonify

uri = 'http://api.urbandictionary.com/v0/define?term=%s'
random_uri = 'http://api.urbandictionary.com/v0/random'
error = 'Unable to find definition!'

def urban(code, input):
    # clean and split the input
    try:
        if input.group(2):
            msg = input.group(2).lower().strip()
            tmp = msg.replace('-','').split()
            if tmp[-1].isdigit():
                if int(tmp[-1]) <= 0:
                    id = 0
                else:
                    id = int(tmp[-1].replace('-','')) - 1
                del tmp[-1]
                msg = ' '.join(tmp)
            else:
                id = 0
            data = jsonify(get(uri % quote(msg)).read())['list']
            if not data:
                return code.reply(code.color('red',error))
            max = len(data)
            if id > max:
                id = max
                data = data[max-1]
            else:
                data = data[id]
                id += 1
            msg = '({id} of {max}) "{word}": {definition} +{up}/-{down}'
            if len(data['definition']) > 235:
                data['definition'] = data['definition'][0:235] + '[...]'
            return code.say(msg.format(
                                id=code.color('purple', str(id)),
                                max=code.color('purple', str(max)),
                                definition=strp(data['definition']),
                                word=code.color('purple', data['word']),
                                up=code.color('red', data['thumbs_up']),
                                down=code.color('red', data['thumbs_down'])
                            ))
            # Begin trying to get the definition
        else:
            # Get a random definition...
            data = jsonify(get(random_uri).read())['list'][0]
            if not data:
                return code.reply(code.color('red',error))
            msg = '(Definition for "{word}"): {definition} +{up}/-{down}'
            if len(data['definition']) > 235:
                data['definition'] = data['definition'][0:235] + '[...]'
            return code.say(msg.format(
                                definition=strp(data['definition']),
                                word=code.color('purple', data['word']),
                                up=code.color('red', data['thumbs_up']),
                                down=code.color('red', data['thumbs_down'])
                            ))
    except:
        return code.reply(code.color('red', 'Failed to pull definition from urbandictionary.com!'))
urban.commands = ['urban', 'ud']
urban.example = '.urban liam'


def strp(data):
    data = data.replace('\n', ' ').replace('\r','')
    while '  ' in data:
        data = data.replace('  ', ' ')
    return data.strip()

if __name__ == '__main__':
    print __doc__.strip()