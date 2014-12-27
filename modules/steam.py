from util import web
import re
from util.hook import *

userid_re = r'.*(?:steamcommunity.com|www.steamcommunity.com)/(?:profiles|id)/([-_a-zA-Z0-9]+)/?.*'
appid_re = r'.*(?:store.steampowered.com|steamcommunity.com|steamdb.info)/app/([0-9]+)/?.*'

# Most of this file is done by manually parsing to get around having to use API keys, and as such,
#  steamdb is unlikely to change their html tables much


@hook(cmds=['steam'], args=True)
def steam_user(code, input):
    """ steam <id> -- find user information and worth of a Steam account/username """
    user_lookup(code, input.group(2))


@hook(rule=userid_re)
def steam_user_auto(code, input):
    user_lookup(code, input.group(1), showerror=False)


def user_lookup(code, id, showerror=True):
    try:
        data = web.text('http://steamdb.info/calculator/?player={id}&currency=us'.format(id=id), timeout=10)
        if 'This profile is private, unable to retrieve owned games.' in data:
            if showerror:
                code.say('{b}Unabled to retrieve info, that account is {red}private{c}!')
            return
        realname = re.search(r'<title>(?P<name>.*?) \xb7 .*?</title>', data).group('name')
        status = re.search(
            r'<td class="span2">Status</td>.*?<td>(?P<status>.*?)</td>', data).group('status')
        # Basic user information
        details = data.split('[list]')[1].split('[/list]')[0]
        details = re.sub(r'\<\/.*?\>', '', details)
        details = re.sub(r'\<.*?\>', ' {b}- ', details)
        details = re.sub(r'\[.*?\]', '', details)
        details = details.replace(': ', ': {b}')
        url = 'http://steamcommunity.com/id/' + id
        return code.say('{b}%s{b} - {green}%s{c} - %s - %s' % (web.escape(realname), web.striptags(status), details, url))
    except:
        if showerror:
            code.say('{b}Unable to find user information on %s!' % id)
        return


@hook(rule=appid_re, supress=True)
def steam_app_auto(code, input):
    data = web.text('http://steamdb.info/app/%s/' % web.quote(input.group(1)), timeout=10)
    output = []
    output.append(
        re.findall(r'<td>Name</td><td itemprop="name">(.*?)</td>', data)[0])  # Name

    # Metacritic Score
    score = re.findall(r'metacritic_score</td><td>(.*?)</td>', data)
    if len(score) < 1:
        output.append('Rating: N/A')
    else:
        output.append('Rating: %s/100' % score[0])

    # Released yet?
    if re.search(r'(?im)<td .*?>releasestate</td><td>prerelease</td>', data):
        output.append('{blue}Prerelease{c}')

    # OS List
    if '<td class="span3">oslist</td>' in data:
        tmp = re.findall(
            r'<tr><td class="span3">oslist</td><td>(.*?)</td></tr>', data)[0]
        tmp = re.findall(r'title="(.*?)"', tmp)
        output.append('OS: ' + ', '.join(tmp))
    else:
        output.append('OS: N/A')

    # With pricing, there are a few options...
    # 1. Free, 2. Cost, 3. Cost with discount
    # As well, 1. Not released (May cause issues with rendering the price
    # table) or 2. released
    if re.search(r'(?im)<td .*?>isfreeapp</td>.*?<td>Yes</td>', data):
        output.append('{green}Free{c}')
    else:
        tmp = re.findall(  # e.g. $19.99 at -20%
            r'<img .*? alt="us".*?> U.S. Dollar</td><td .*?>(?P<price>.*?)</td>' +
            '<td .*?>Base Price</td><td .*?>(?P<lowest>.*?)</td></tr>', data)[0][0]
        tmp = re.sub(r'^(?P<price>\$[0-9,.-]{2,6})$', r'{green}\g<price>{c}', tmp)
        tmp = re.sub(
            r'(?P<price>\$[0-9,.-]{2,6}) at (?P<discount>\-[0-9.]{1,3}\%)',
            r'{green}\g<price>{c} ({red}\g<discount>{c})', web.striptags(tmp))
        output.append(tmp)

    output.append('http://store.steampowered.com/app/%s/' %
                  re.findall(r'<td class="span3">App ID</td><td>(.*?)</td>', data)[0])

    return str(' - {b}'.join(output).replace(': ', ': {b}'))
