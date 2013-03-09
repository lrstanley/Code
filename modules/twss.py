#!/usr/bin/env python
"""
Stan-Derp Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
twss.py - Stan-Derp 'That's what she said' Module
http://standerp.liamstanley.net/
"""

import urllib2
import re
import os
import sys


last = "DEBUG_ME" # Dont find this in terminal, you might want to flip shit.

if not os.path.exists("modules/twss.txt"):
    f = open("modules/twss.txt", "w")
    url = "http://www.twssstories.com/best?page="
    first_re = re.compile(r"<p>.+TWSS\.*</p>")
    inner_re = re.compile(r'".+"')
    url2 = "http://www.shesaidit.ca/index.php?pageno="
    second_re = re.compile(r'"style30">.*</span>')

    print "Now creating TWSS database. This will take a few minutes.",
    for page in range(1,148):
        sys.stdout.flush()
        print ".",
        curr_url = url + str(page)
        html = urllib2.urlopen(curr_url)
        story_list = first_re.findall(html.read())
        for story in story_list:
            if len(inner_re.findall(story)) > 0:
                lowercase =  inner_re.findall(story)[0].lower()
                f.write(re.sub("[^\w\s]", "", lowercase) + "\n")

    for page in range(1,146):
        sys.stdout.flush()
        print ".",
        curr_url = url2 + str(page)
        html = urllib2.urlopen(curr_url)
        matches_list = second_re.findall(html.read())
        for match in matches_list:
             lowercase = match[10:-7].lower().strip()
             if len(inner_re.findall(lowercase)) > 0:
                 lowercase = inner_re.findall(lowercase)[0]
             f.write(re.sub("[^\w\s]", "", lowercase) + "\n")
    f.close()


def say_it(standerp, input):
    global last
    user_quotes = None
    with open("modules/twss.txt") as f:
        scraped_quotes = frozenset([line.rstrip() for line in f])
    if os.path.exists("modules/twss_user_added.txt"):
        with open("modules/twss_user_added.txt") as f2:
            user_quotes = frozenset([line.rstrip() for line in f2])
    quotes = scraped_quotes.union(user_quotes) if user_quotes else scraped_quotes
    formatted = input.group(1).lower()
    if re.sub("[^\w\s]", "", formatted) in quotes:
        standerp.say("That's what she said.")
    last = re.sub("[^\w\s]", "", formatted)
say_it.rule = r"(.*)"
say_it.priority = "low"

def add_twss(standerp, input):
    print last
    with open("modules/twss_user_added.txt", "a") as f:
        f.write(re.sub(r"[^\w\s]", "", last.lower()) + "\n")
        f.close()
    standerp.say("That's what she said.")
add_twss.commands = ["twss"]
add_twss.priority = "low"
add_twss.threading = False

if __name__ == '__main__':
    print __doc__.strip()
