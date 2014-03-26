#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
urban.py - Code Urban Dictionary Module
http://code.liamstanley.io/
"""

from urllib2 import urlopen as get
from urllib import quote
from json import loads as jsonify

uri = 'http://api.urbandictionary.com/v0/define?term=%s'
random_uri = 'http://api.urbandictionary.com/v0/random'
error = '{red}{b}Unable to find definition!'

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
                return code.reply(error)
            max = len(data)
            if id > max:
                id = max
                data = data[max-1]
            else:
                data = data[id]
                id += 1
            msg = '({purple}{id}{c} of {purple}{max}{c}) "{purple}{word}{c}": {definition} +{red}{up}{c}/-{red}{down}{c}'
            if len(data['definition']) > 235:
                data['definition'] = data['definition'][0:235] + '[...]'
            return code.say(code.format(msg).format(
                                id=str(id), max=str(max), definition=strp(data['definition']),
                                word=data['word'], up=str(data['thumbs_up']), down=str(data['thumbs_down'])
                            ))
            # Begin trying to get the definition
        else:
            # Get a random definition...
            data = jsonify(get(random_uri).read())['list'][0]
            if not data:
                return code.reply(error)
            msg = '(Definition for "{purple}{word}{c}"): {definition} +{red}{up}{c}/-{red}{down}{c}'
            if len(data['definition']) > 235:
                data['definition'] = data['definition'][0:235] + '[...]'
            return code.say(code.format(msg).format(
                                definition=strp(data['definition']), word=data['word'],
                                up=str(data['thumbs_up']), down=str(data['thumbs_down'])
                            ))
    except:
        return code.reply('{red}{b}Failed to pull definition from urbandictionary.com!')
urban.commands = ['urban', 'ud']
urban.example = 'urban liam 2'


def strp(data):
    data = data.replace('\n', ' ').replace('\r','')
    while '  ' in data:
        data = data.replace('  ', ' ')
    return data.strip()

if __name__ == '__main__':
    print __doc__.strip()