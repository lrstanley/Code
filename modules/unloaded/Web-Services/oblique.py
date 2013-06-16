#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
oblique.py - Code Web Services Interface
http://code.liamstanley.net/
"""

import re, urllib
import web

definitions = 'https://github.com/nslater/oblique/wiki'

r_item = re.compile(r'(?i)<li>(.*?)</li>')
r_tag = re.compile(r'<[^>]+>')

def mappings(uri):
    result = {}
    bytes = web.get(uri)
    for item in r_item.findall(bytes):
        item = r_tag.sub('', item).strip(' \t\r\n')
        if not ' ' in item: continue

        command, template = item.split(' ', 1)
        if not command.isalnum(): continue
        if not template.startswith('http://'): continue
        result[command] = template.replace('&amp;', '&')
    return result

def service(code, input, command, args):
    t = o.services[command]
    template = t.replace('${args}', urllib.quote(args.encode('utf-8'), ''))
    template = template.replace('${nick}', urllib.quote(input.nick, ''))
    uri = template.replace('${sender}', urllib.quote(input.sender, ''))

    info = web.head(uri)
    if isinstance(info, list):
        info = info[0]
    if not 'text/plain' in info.get('content-type', '').lower():
        return code.reply(code.color('red', 'Sorry, the service didn\'t respond in plain text.'))
    bytes = web.get(uri)
    lines = bytes.splitlines()
    if not lines:
        return code.reply(code.color('red', 'Sorry, the service didn\'t respond any output.'))
    try: line = lines[0].encode('utf-8')[:350]
    except: line = lines[0][:250]
#    if input.group(1) == 'urban':
#        if line.find('ENOTFOUND') > -1:
#            line = "I'm sorry, that definition %s found." % code.bold('wasn\'t')
#            code.say(line)
#        elif line.find('Traceback (most recent call last)') > -1:
#            line = code.color('red', 'Failed to search for that definition. Please try again.')
#            code.say(line)
#        else:
#            code.say(line)

def refresh(code):
    if hasattr(code.config, 'services'):
        services = code.config.services
    else: services = definitions

    old = o.services
    o.serviceURI = services
    o.services = mappings(o.serviceURI)
    return len(o.services), set(o.services) - set(old)

def o(code, input):
    """Call a webservice."""
    if input.group(1) == 'whois':
        text = 'whois ' + input.group(2)
    else:
        text = input.group(2)

    if (not o.services) or (text == 'refresh'):
        length, added = refresh(code)
        if text == 'refresh':
            msg = 'Okay, found %s services.' % code.bold(length)
            if added:
                msg += ' Added: ' + ', '.join(sorted(added)[:5])
                if len(added) > 5: msg += ', &c.'
            return code.reply(msg)

    if not text:
        return code.reply('Try %s for details.' % code.bold(o.serviceURI))

    if ' ' in text:
        command, args = text.split(' ', 1)
    else: command, args = text, ''
    command = command.lower()

    if command == 'service':
        msg = o.services.get(args, code.bold('No such service!'))
        return code.reply(msg)

    if not o.services.has_key(command):
        return code.reply('Service not found in %s' % code.bold(o.serviceURI))

    if hasattr(code.config, 'external'):
        default = code.config.external.get('*')
        manifest = code.config.external.get(input.sender, default)
        if manifest:
            commands = set(manifest)
            if (command not in commands) and (manifest[0] != '!'):
                return code.reply('Sorry, %s is not whitelisted' % code.bold(command))
            elif (command in commands) and (manifest[0] == '!'):
                return code.reply('Sorry, %s is blacklisted' % code.bold(command))
    service(code, input, command, args)
o.commands = ['o', 'whois']
o.example = '.o servicename arg1 arg2 arg3'
o.services = {}
o.serviceURI = None

def snippet(code, input):
    if not o.services:
        refresh(code)

    search = urllib.quote(input.group(2).encode('utf-8'))
    py = "BeautifulSoup.BeautifulSoup(re.sub('<.*?>|(?<= ) +', '', " + \
          "''.join(chr(ord(c)) for c in " + \
          "eval(urllib.urlopen('https://ajax.googleapis.com/ajax/serv" + \
          "ices/search/web?v=1.0&q=" + search + "').read()" + \
          ".replace('null', 'None'))['responseData']['resul" + \
          "ts'][0]['content'].decode('unicode-escape')).replace(" + \
          "'&quot;', '\x22')), convertEntities=True)"
    service(code, input, 'py', py)
snippet.commands = ['snippet']

if __name__ == '__main__':
    print __doc__.strip()
