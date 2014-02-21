"""
Code Copyright (C) 2012-2014 Liam Stanley
github.py - Code Github Module
http://code.liamstanley.io/
"""

from datetime import datetime
from subprocess import *
import json, urllib2

repo_api = 'https://api.github.com/repos/%s' # Username/Repo
user_api = 'https://api.github.com/users/%s' # Username


def github(code, input):
    syntax = 'Syntax: \'.github <user|user repo>\''
    failed = 'Failed to get data from Githubs API :('
    if not input.group(2):
        return code.say(syntax)

    if len(input.group(2).strip().split()) != 1:
        return code.say(syntax)
    
    spacer = ' %s ' % code.color('blue','|')

    if not '/' in input.group(2):
        # Assume a single username
        try:
            response = json.loads(urllib2.urlopen(user_api % input.group(2).strip()).read())
            print response
        except:
            return code.say(failed)
        if 'message' in response:
            # Assume failed
            return code.say(failed)
        # Here is where we build the response
        output = []
        output.append('%s (%s)' % (response['name'], response['login']))
        if 'location' in response:
            output.append(response['location'])
        if 'email' in response:
            if response['email'] != 'null':
                output.append(response['email'])
        if 'public_repos' in response:
            output.append('%s Repos' % response['public_repos'])
        if 'followers' in response:
            output.append('%s Followers' % response['followers'])
        if 'following' in response:
            output.append('Following %s' % response['following'])
        if 'public_gists' in response:
            output.append('%s Gists' % response['public_gists'])
        if 'html_url' in response:
            output.append(response['html_url'])
        
        return code.say(spacer.join(output))
      
    else:
        # Assume Username/Repo
        try:
            response = json.loads(urllib2.urlopen(repo_api % input.group(2).strip()).read())
        except:
            return code.say(failed)
        if 'message' in response:
            # Assume failed
            return code.say(failed)
        # Here is where we build the response
        output = []
        output.append('%s (%s)' % (response['name'], response['owner']['login']))
        output.append(response['description'])
        output.append('%s %s' % (response['stargazers_count'],u'\u2605'))
        output.append('%s %s' % (response['watchers_count'],u'\u231A'))
        output.append('%s %s' % (response['forks_count'],u'\u2442'))
        output.append('%s %s' % (response['open_issues_count'],u'\u2602'))
        output.append('%s %s' % (response['network_count'],u'\U0001F46C'))
        output.append('%s %s' % (response['subscribers_count'],u'\u2764'))
        output.append(response['html_url'])
        return code.say(spacer.join(output))
github.commands = ['github','git']
github.priority = 'medium'
github.rate = '15'


def git_info():
    p = Popen(["git", "log", "-n 1"], stdout=PIPE, close_fds=True)

    commit = p.stdout.readline()
    author = p.stdout.readline()
    date = p.stdout.readline()
    return commit, author, date


def version(code, input):
    try:
        commit, author, date = git_info()
        code.say(str(input.nick) + ": running version:")
        code.say('  ' + commit)
        code.say('  ' + author)
        code.say('  ' + date)
        code.say('  ' + code.bold('Source: ') + 'https://github.com/Liamraystanley/Code/')
    except:
        code.say('%s does not use Github file management. Unable to determine version.' % code.nick)
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
    text = text.replace('PING ', '')
    text = text.replace('\x01', '')
    code.write(('NOTICE', input.nick),
            '\x01PING {0}\x01'.format(text))
ctcp_ping.rule = '\x01PING\s(.*)\x01'
ctcp_ping.rate = 10


def ctcp_time(code, input):
    dt = datetime.now()
    current_time = dt.strftime('%A, %d. %B %Y %I:%M%p')
    code.write(('NOTICE', input.nick),
            '\x01TIME {0}\x01'.format(current_time))
ctcp_time.rule = '\x01TIME\x01'
ctcp_time.rate = 20

if __name__ == '__main__':
    print __doc__.strip()