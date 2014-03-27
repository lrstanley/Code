#!/usr/bin/env python
'''
Code Copyright (C) 2012-2014 Liam Stanley
admin.py - Code TLD Module
http://code.liamstanley.io/
'''

import util.web
from util.hook import *
import re


uri = 'https://en.wikipedia.org/wiki/List_of_Internet_top-level_domains'
r_tag = re.compile(r'<(?!!)[^>]+>')


@hook(cmds=['tld'], ex='tld net')
def gettld(code, input):
    """tld <shorthand> -- Show information about the given Top Level Domain."""
    page = util.web.get(uri).read()
    search = r'(?i)<td><a href="\S+" title="\S+">\.{0}</a></td>\n(<td><a href=".*</a></td>\n)?<td>([A-Za-z0-9].*?)</td>\n<td>(.*)</td>\n<td[^>]*>(.*?)</td>\n<td[^>]*>(.*?)</td>\n'
    search = search.format(input.group(2))
    re_country = re.compile(search)
    matches = re_country.findall(page)
    if not matches:
        search = r'(?i)<td><a href="\S+" title="(\S+)">\.{0}</a></td>\n<td><a href=".*">(.*)</a></td>\n<td>([A-Za-z0-9].*?)</td>\n<td[^>]*>(.*?)</td>\n<td[^>]*>(.*?)</td>\n'
        search = search.format(input.group(2))
        re_country = re.compile(search)
        matches = re_country.findall(page)
    if matches:
        matches = list(matches[0])
        i = 0
        while i < len(matches):
            matches[i] = r_tag.sub("", matches[i])
            i += 1
        desc = matches[2]
        if len(desc) > 400:
            desc = desc[:400] + "..."
        reply = "%s -- %s. IDN: %s, DNSSEC: %s" % (matches[1], desc,
                matches[3], matches[4])
        code.reply(reply)
    else:
        search = r'<td><a href="\S+" title="\S+">.{0}</a></td>\n<td><span class="flagicon"><img.*?\">(.*?)</a></td>\n<td[^>]*>(.*?)</td>\n<td[^>]*>(.*?)</td>\n<td[^>]*>(.*?)</td>\n<td[^>]*>(.*?)</td>\n<td[^>]*>(.*?)</td>\n'
        search = search.format(unicode(input.group(2)))
        re_country = re.compile(search)
        matches = re_country.findall(page)
        if matches:
            matches = matches[0]
            dict_val = dict()
            dict_val["country"], dict_val["expl"], dict_val["notes"], dict_val["idn"], dict_val["dnssec"], dict_val["sld"] = matches
            for key in dict_val:
                if dict_val[key] == "&#160;":
                    dict_val[key] = "N/A"
                dict_val[key] = r_tag.sub('', dict_val[key])
            if len(dict_val["notes"]) > 400:
                dict_val["notes"] = dict_val["notes"][:400] + "..."
            reply = "%s (%s, %s). IDN: %s, DNSSEC: %s, SLD: %s" % (dict_val["country"], dict_val["expl"],
                 dict_val["notes"], dict_val["idn"], dict_val["dnssec"], dict_val["sld"])
        else:
            reply = "No matches found for TLD: {0}".format(unicode(input.group(2)))
        code.say(reply)


if __name__ == '__main__':
    print __doc__.strip()
