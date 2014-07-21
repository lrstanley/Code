from util.hook import *
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
