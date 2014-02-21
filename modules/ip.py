#!/usr/bin/env python
# coding=utf-8
"""
Code Copyright (C) 2012-2014 Liam Stanley
ip.py - Code IP lookup Module
http://code.liamstanley.io/
"""

from modules import unicode as uc
import json, re
import socket, web, urllib2

base = 'http://geo.liamstanley.io/json/%s'
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
    page = web.get(base % txt)
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


def test(code, input):
    """GeoIP user on join."""
    if hasattr(code.config, 'geoip'):
        ip = code.config.geoip
        if not ip:
            return

        # Make them all lowercase
        allowed = []
        for channel_name in ip:
            allowed.append(channel_name.lower())

        # Split the line and get all the data
        host, command, channel = code.raw.split('@')[1].split()

        # Stop if the host is suspicious....
        bad = ['proxy','clone','bnc','bouncer','cloud']
        for domain in bad:
            if domain in host.lower():
                return

        if input.nick == code.nick or not channel.lower() in allowed:
            return
        try:
            r = json.loads(urllib2.urlopen(base % host).read())
            output = []
            #{u'city': u'Holt', u'region_code': u'MI', u'region_name': u'Michigan', u'areacode': u'517',
            # u'ip': u'68.40.234.141', u'zipcode': u'48842', u'longitude': -84.5377, u'metro_code': u'551',
            # u'latitude': 42.6333, u'country_code': u'US', u'country_name': u'United States'}
            location = ['region_name', 'country_name']
            for val in location:
                if val in r:
                    output.append(r[val])
            if not r['city']:
                rough = '(estimated)'
            else:
                rough = ''
            return code.msg(channel, 'User is connecting from %s%s' % (', '.join(output), rough))
        except:
            return
    else:
        return # It's not enabled... :(
test.event = 'JOIN'
test.rule = r'.*'

if __name__ == '__main__':
    print __doc__.strip()
