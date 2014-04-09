#!/usr/bin/env python
# coding=utf-8
"""
Code Copyright (C) 2012-2014 Liam Stanley
ip.py - Code IP lookup Module
http://code.liamstanley.io/
"""

from socket import getfqdn as rdns
from util.hook import *
from util import web

base = 'http://geo.liamstanley.io/json/%s'


@hook(cmds=['ip', 'host', 'whois', 'geo', 'geoip'], ex='whois 8.8.8.8')
def ip(code, input):
    """whois <ip|hostname> - Reverse domain/ip lookup (WHOIS)"""
    show = [
        ['hostname', 'Hostname'],
        ['ip', 'IP'],
        ['city', 'City'],
        ['region_name', 'Region'],
        ['country_name', 'Country'],
        ['zipcode', 'Zip'],
        ['latitude', 'Lat'],
        ['longitude', 'Long']
    ]
    doc = {
        'invalid': '{red}Invalid input: \'.whois [ip|hostname]\'{c}',
        'error': '{red}Couldn\'t receive information for %s{c}',
        'na': '{red}N/A{c}'
    }
    if not input.group(2):
        host = input.host.strip()
    else:
        host = input.group(2).strip()
    if '.' not in host and ':' not in host and len(host.split()) != 1:
        return code.reply(doc['invalid'])
    host = code.stripcolors(host).encode('ascii', 'ignore')

    # Try to get data from GeoIP server...
    try:
        data = web.json(base % host, timeout=4)
    except:
        return code.reply(doc['error'] % host)

    # Check if errored or localhost
    if data['country_name'] == 'Reserved':
        return code.reply(doc['error'] % host)

    # Try to get reverse dns based hostname
    data['hostname'], output = rdns(host), []

    # Make list of things to respond with
    for option in show:
        if len(str(data[option[0]])) < 1 or data[option[0]] == host:
            output.append('{blue}%s{c}: %s' % (option[1], doc['na']))
            continue
        output.append('{blue}%s{c}: %s' % (option[1], data[option[0]]))
    return code.say(' \x02|\x02 '.join(output))


@hook(rule=r'.*', event='JOIN', rate=10)
def geoip(code, input):
    """GeoIP user on join."""
    if not hasattr(code.config, 'geoip'):
        return
    if not code.config.geoip:
        return

    allowed = []
    for channel_name in code.config.geoip:
        allowed.append(channel_name.lower())

    # Split the line and get all the data
    try:
        host, command, channel = code.raw.split('@')[1].split()
    except:
        return

    for domain in ['proxy', 'clone', 'bnc', 'bouncer', 'cloud', 'server']:
        if domain in host.lower():
            return

    if input.nick == code.nick or not channel.lower() in allowed:
        return
    try:
        r = web.json(base % host, timeout=4)
        output, location = [], ['region_name', 'country_name']
        for val in location:
            if val not in r:
                continue
            if len(r[val]) > 1:
                output.append(r[val])
        if not r['city']:
            rough = ' (estimated)'
        else:
            rough = ''
        return code.msg(channel, '{green}User is connecting from %s%s' % (', '.join(output), rough))
    except:
        return
