from util.hook import *
from util import web

repo_api = 'https://api.github.com/repos/%s'  # Username/Repo
user_api = 'https://api.github.com/users/%s'  # Username


github_regex = r'.*https?://.*?github\.com\/(.*)'


@hook(rule=github_regex, thread=False)
def github_automatic(code, input):
    """Automatically find the information from a github url and display it
       to users in a channel"""
    try:
        github(code, input, input.group(0).split('.com/', 1)[1].strip('/'), auto=True)
    except:
        return


@hook(cmds=['github', 'git'], ex='github Liamraystanley/Code', rate=15, args=True)
def github_cmd(code, input):
    return github(code, input, input.group(2))


def github(code, input, message, auto=False):
    """github <user}user/repo> - Get username data, or user/repo data from Github"""
    syntax = 'Syntax: \'.github <user|user/repo>\''
    failed = 'Failed to get data from Githubs API :('
    if len(message.strip().split()) != 1:
        if not auto:
            code.say(syntax)
        return

    spacer = ' {blue}|{c} '

    if '/' not in message:
        # Assume a single username
        try:
            tmp = web.json(user_api % message.strip())
            response = {}
            # Remove dem ugly nulled values. It's a dictionary so we have to
            # loop differently.
            for key, value in tmp.iteritems():
                if value != '' or len(value) != 0 or value.lower() != 'null':
                    response[key] = value
        except:
            if not auto:
                code.say(failed)
            return
        if 'message' in response:
            # Assume failed
            if not auto:
                code.say(failed)
            return

        # Here is where we build the response
        output = []
        if 'name' in response:
            if response['name'].lower() == 'null' and auto:
                # Assume subdomain.. or something. I dunno.
                return
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
            response = web.json(repo_api % message.strip())
        except:
            if not auto:
                code.say(failed)
            return
        if 'message' in response:
            # Assume failed
            if not auto:
                code.say(failed)
            return
        # Here is where we build the response
        output = []
        output.append('%s (%s)' % (response['name'], response['owner']['login']))
        output.append(response['description'])

        def is_multiple(number, word):
            if str(number) != '1':
                word += 's'
            return '%s %s' % (str(number), word)

        output.append(is_multiple(response['stargazers_count'], 'star'))
        output.append(is_multiple(response['watchers_count'], 'watcher'))
        output.append(is_multiple(response['forks_count'], 'fork'))
        output.append(is_multiple(response['open_issues_count'], 'issue'))
        output.append(is_multiple(response['network_count'], 'collaborator'))
        output.append(is_multiple(response['subscribers_count'], 'subscriber'))
        output.append(response['html_url'])
        return code.say(spacer.join(output))
