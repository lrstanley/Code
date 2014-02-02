#!/usr/bin/env python
# coding=utf-8
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
ip.py - Code IP lookup Module
http://code.liamstanley.io/
"""

from modules import unicode as uc
import json
import re
import socket
import web

base = 'http://geo.liamstanley.io/json/'
re_ip = re.compile('(?i)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')


def ip(code, input):
    txt = input.group(2)
    if not txt:
        return code.reply(code.color('red', 'No search term!'))
    elif txt.find('192.168.0.') > -1 or txt.find('127.0.0.') > -1:
        return code.reply(code.color('red', 'That IP is blacklisted!'))
    elif not '.' in txt and not ':' in txt:
        return code.reply(code.color('red','Incorrect input!'))
    txt = uc.encode(txt)
    query = uc.decode(txt) 
    response = ''
    #response = '[' + code.color('blue', 'IP/Host Lookup ') + '] '
    page = web.get(base + txt)
    try:
        results = json.loads(page)
    except:
        print str(page)
        return code.color('red', code.reply('Couldn\'t receive information for %s' % code.bold(txt)))
    if results:
        print 'query', str(query)
        print 'matches', re_ip.findall(query)
        if re_ip.findall(query):
            ## IP Address
            try:
                hostname = socket.gethostbyaddr(query)[0]
            except:
                hostname = code.bold(code.color('red', 'Unknown Host'))
            response += code.color('blue', 'Hostname: ') + str(hostname)
        else:
            ## Host name
            response += code.bold(code.color('blue','IP: ')) + results['ip']
        spacing = ' ' + code.bold('|')
        for param in results:
            if not results[param]:
                results[param] = code.bold(code.color('red', 'N/A'))
        if 'city' in results:
            response += '%s %s %s' % (spacing, code.bold(code.color('blue', 'City:')), results['city'])
        if 'region_name' in results:
            response += '%s %s %s' % (spacing, code.bold(code.color('blue', 'State:')), results['region_name'])
        if 'country_name' in results:
            response += '%s %s %s' % (spacing, code.bold(code.color('blue', 'Country:')), results['country_name'])
        if 'zip' in results:
            response += '%s %s %s' % (spacing, code.bold(code.color('blue', 'ZIP:')), results['zip'])
        response += '%s %s %s' % (spacing, code.bold(code.color('blue', 'Latitude:')), results['latitude'])
        response += '%s %s %s' % (spacing, code.bold(code.color('blue', 'Longitude:')), results['longitude'])
    code.reply(response)
ip.commands = ['ip', 'iplookup', 'host', 'whois']
ip.example = ".iplookup 8.8.8.8"

if __name__ == '__main__':
    print __doc__.strip()
