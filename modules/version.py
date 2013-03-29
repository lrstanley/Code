"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
version.py - Code Version Module
http://code.liamstanley.net/
"""

from datetime import datetime
from subprocess import *


def git_info():
    p = Popen(["git", "log", "-n 1"], stdout=PIPE, close_fds=True)

    commit = p.stdout.readline()
    author = p.stdout.readline()
    date = p.stdout.readline()
    return commit, author, date


def version(code, input):
    commit, author, date = git_info()

    code.say(str(input.nick) + ": running version:")
    code.say("  " + commit)
    code.say("  " + author)
    code.say("  " + date)
version.commands = ['version']
version.priority = 'medium'
version.rate = 30


def ctcp_version(code, input):
    commit, author, date = git_info()
    date = date.replace("  ", "")

    code.write(('NOTICE', input.nick),
            '\x01VERSION {0} : {1}\x01'.format(commit, date))
ctcp_version.rule = '\x01VERSION\x01'
ctcp_version.rate = 20


def ctcp_source(code, input):
    code.write(('NOTICE', input.nick),
            '\x01SOURCE https://github.com/Liamraystanley/Code/\x01')
    code.write(('NOTICE', input.nick),
            '\x01SOURCE\x01')
ctcp_source.rule = '\x01SOURCE\x01'
ctcp_source.rate = 20


def ctcp_ping(code, input):
    text = input.group()
    text = text.replace("PING ", "")
    text = text.replace("\x01", "")
    code.write(('NOTICE', input.nick),
            '\x01PING {0}\x01'.format(text))
ctcp_ping.rule = '\x01PING\s(.*)\x01'
ctcp_ping.rate = 10


def ctcp_time(code, input):
    dt = datetime.now()
    current_time = dt.strftime("%A, %d. %B %Y %I:%M%p")
    code.write(('NOTICE', input.nick),
            '\x01TIME {0}\x01'.format(current_time))
ctcp_time.rule = '\x01TIME\x01'
ctcp_time.rate = 20

if __name__ == '__main__':
    print __doc__.strip()
