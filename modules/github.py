from datetime import datetime
from util.hook import *
from subprocess import *
from util import web

repo_api = 'https://api.github.com/repos/%s'  # Username/Repo
user_api = 'https://api.github.com/users/%s'  # Username


@hook(cmds=['github', 'git'], ex='github Liamraystanley/Code', rate=15, args=True)
def github(code, input):
    """github <user}user/repo> - Get username data, or user/repo data from Github"""
    syntax = 'Syntax: \'.github <user|user/repo>\''
    failed = 'Failed to get data from Githubs API :('
    if len(input.group(2).strip().split()) != 1:
        return code.say(syntax)

    spacer = ' {blue}|{c} '

    if '/' not in input.group(2):
        # Assume a single username
        try:
            tmp = web.json(user_api % input.group(2).strip())
            response = {}
            # Remove dem ugly nulled values. It's a dictionary so we have to
            # loop differently.
            for key, value in tmp.iteritems():
                if value != '' or len(value) != 0 or value != 'null':
                    response[key] = value
            print response
        except:
            return code.say(failed)
        if 'message' in response:
            # Assume failed
            return code.say(failed)

        # Here is where we build the response
        output = []
        if 'name' in response:
            output.append('%s (%s)' % (response['name'], response['login']))
        else:
            output.append(response['login'])
        if 'location' in response:
            output.append(response['location'])
        if 'email' in response:
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
            response = jweb.json(repo_api % input.group(2).strip())
        except:
            return code.say(failed)
        if 'message' in response:
            # Assume failed
            return code.say(failed)
        # Here is where we build the response
        output = []
        output.append('%s (%s)' %
                      (response['name'], response['owner']['login']))
        output.append(response['description'])
        output.append('%s %s' % (response['stargazers_count'], u'\u2605'))
        output.append('%s %s' % (response['watchers_count'], u'\u231A'))
        output.append('%s %s' % (response['forks_count'], u'\u2442'))
        output.append('%s %s' % (response['open_issues_count'], u'\u2602'))
        output.append('%s %s' % (response['network_count'], u'\U0001F46C'))
        output.append('%s %s' % (response['subscribers_count'], u'\u2764'))
        output.append(response['html_url'])
        return code.say(spacer.join(output))


def git_info():
    p = Popen(["git", "log", "-n 1"], stdout=PIPE, close_fds=True)

    commit = p.stdout.readline()
    author = p.stdout.readline()
    date = p.stdout.readline()
    return commit, author, date


@hook(cmds=['version', 'v'], rate=30)
def version(code, input):
    """Try to get version (commit) data from git (if installed)"""
    try:
        commit, author, date = git_info()
        code.say(str(input.nick) + ": running version:")
        code.say('  ' + commit)
        code.say('  ' + author)
        code.say('  ' + date)
        code.say('  ' +
                 '{b}Source:{b} https://github.com/Liamraystanley/Code/')
    except:
        code.say(
            '%s does not use Github file management. Unable to determine version.' %
            code.nick)


@hook(rule='\x01VERSION\x01', rate=20)
def ctcp_version(code, input):
    commit, author, date = git_info()
    date = date.replace("  ", "")

    code.write(
        ('NOTICE', input.nick), '\x01VERSION {0} : {1}\x01'.format(
            commit, date)
    )


@hook(rule='\x01SOURCE\x01', rate=20)
def ctcp_source(code, input):
    code.write(
        ('NOTICE',
         input.nick), '\x01SOURCE https://github.com/Liamraystanley/Code/\x01'
    )
    code.write(
        ('NOTICE', input.nick), '\x01SOURCE\x01'
    )


@hook(rule='\x01PING\s(.*)\x01', rate=10)
def ctcp_ping(code, input):
    text = input.group()
    text = text.replace('PING ', '')
    text = text.replace('\x01', '')
    code.write(
        ('NOTICE', input.nick), '\x01PING {0}\x01'.format(text)
    )


@hook(rule='\x01TIME\x01', rate=20)
def ctcp_time(code, input):
    dt = datetime.now()
    current_time = dt.strftime('%A, %d. %B %Y %I:%M%p')
    code.write(
        ('NOTICE', input.nick), '\x01TIME {0}\x01'.format(current_time)
    )
