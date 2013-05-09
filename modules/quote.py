#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
quote.py - Code Quote Module
http://code.liamstanley.net/
"""

import re
import web

quoteuri = 'http://www.leonatkinson.com/random/index.php/rest.html?method=advice'
r_paragraph = re.compile(r'<quote>.*?</quote>')


def getquote(code, input):
    page = web.get(quoteuri)
    paragraphs = r_paragraph.findall(page)
    line = re.sub(r'<[^>]*?>', '', unicode(paragraphs[0]))
    code.say(code.bold(line.lower().capitalize() + "."))
getquote.commands = ['quote']
getquote.thread = False
getquote.rate = 30

if __name__ == '__main__':
    print __doc__.strip()
