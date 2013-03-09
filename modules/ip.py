#!/usr/bin/env python
# coding=utf-8
"""
Stan-Derp Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
ip.py - Stan-Derp IP lookup Module
http://standerp.liamstanley.net/

This module has been imported from Willie.
"""

import re
import socket
import web

base = "http://whatismyipaddress.com/ip/"
r_tag = re.compile(r'<(?!!)[^>]+>')

def grab_info(ip):
    rdict = dict()
    answer = web.get(base + ip)
    if answer:
        results = re.compile("th>(\S+?):<.*?<td>(.*?)</td>").findall(answer)
        for x in results:
            rdict[x[0]] = r_tag.sub("", x[1]).strip()
    return rdict

def gen_response(rdict, ip=False):
    response = str()
    if not ip:
        response = "Hostname: " + rdict['Hostname']
    response += " | ISP: " + rdict['ISP']
    response += " | Organization: " + rdict['Organization']
    response += " | Type: " + rdict['Type']
    response += " | Assignment: " + rdict['Assignment']
    response += " | Location: " + rdict['City']
    response += ", " + rdict['State/Region']
    response += ", " + rdict['Country'] + "."
    return response


def getipv4(q):
    resp = str()
    for x in q:
        ip = x[-1][0]
        try:
            resp += gen_response(grab_info(ip), True)
        except:
            continue
        if resp:
            return resp, ip


def ip_lookup(standerp, input):
    hip = input.group(2)
    if not hip:
        return standerp.reply("No search term!")
    query = hip.encode('utf-8')
    answer = grab_info(query)
    response = "[IP/Host Lookup] "
    if answer:
        response += gen_response(answer)
    else:
        response += "Error looking up IP address."
        return
        q = socket.getaddrinfo(query, 80)
        try:
            resp, ip = getipv4(q)
            response += "IP Address: " + str(ip)
            response += resp
        except:
            response += "No results currently found for: %s" % (hip)
    standerp.reply(response)
ip_lookup.commands = ['ip', 'iplookup', 'host', 'whois']
ip_lookup.example = ".iplookup 8.8.8.8"

if __name__ == '__main__':
    print __doc__.strip()
