#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
fucking_dinner.py - Code Fucking Dinner Module
http://code.liamstanley.io/
"""

import re
from urllib2 import urlopen as get
from util.hook import *

uri = 'http://www.whatthefuckshouldimakefordinner.com'
re_mark = re.compile(r'<dt><a href="(.*?)" target="_blank">(.*?)</a></dt>')


@hook(cmds=['fucking_dinner','fd','dinner'], priority='low')
def dinner(code, input):
    """fd -- WHAT DO YOU WANT FOR FUCKING DINNER?"""
    data = get(uri).read()
    results = re_mark.findall(data)
    if not results:
        return code.say('EAT LEFT OVER PIZZA FOR ALL I CARE.')
    url, food = results[0][0], results[0][1]
    code.say('WHY DON\'T YOU EAT SOME FUCKING: %s HERE IS THE RECIPE: %s' % (food, url))