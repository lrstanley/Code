#!/usr/bin/env python
# coding=utf-8
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
ip.py - Code IP Module
http://code.liamstanley.net/
"""

from modules import unicode as uc
import json
import re
import socket
import web

base = 'http://freegeoip.net/json/'
re_ip = re.compile('(?i)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')


def ip_lookup(code, input):
    txt = input.group(2)
    if not txt:
        return code.reply("No search term!")
    txt = uc.encode(txt)
    query = uc.decode(txt)
    response = "[IP/Host Lookup] "
    page = web.get(base + txt)
    try:
        results = json.loads(page)
    except:
        print str(page)
        return code.reply('Did not receive proper JSON from %s' % (base))
    if results:
        print 'query', str(query)
        print 'matches', re_ip.findall(query)
        if re_ip.findall(query):
            ## IP Address
            try:
                hostname = socket.gethostbyaddr(query)[0]
            except:
                hostname = 'Unknown Host'
            response += 'Hostname: ' + str(hostname)
        else:
            ## Host name
            response += 'IP: ' + results['ip']
        spacing = ' |'
        for param in results:
            if not results[param]:
                results[param] = 'N/A'
        if 'city' in results:
            response += '%s City: %s' % (spacing, results['city'])
        if 'region_name' in results:
            response += '%s State: %s' % (spacing, results['region_name'])
        if 'country_name' in results:
            response += '%s Country: %s' % (spacing, results['country_name'])
        if 'zip' in results:
            response += '%s ZIP: %s' % (spacing, results['zip'])
        response += '%s Latitude: %s' % (spacing, results['latitude'])
        response += '%s Longitutde: %s' % (spacing, results['longitude'])
    code.reply(response)
ip_lookup.commands = ['ip', 'iplookup', 'host', 'whois']
ip_lookup.example = ".iplookup 8.8.8.8"

if __name__ == '__main__':
    print __doc__.strip()
