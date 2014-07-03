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
        data = web.get('http://steamdb.info/calculator/?player=%s&currency=us' % id, timeout=10).read()
        if 'This profile is private, unable to retrieve owned games.' in data:
            if showerror:
                code.say('{b}Unabled to retrieve info, that account is {red}private{c}!')
            return
        realname = re.search(r'<title>.*?</title>', data).group().split('>')[1].split(' \xc2\xb7')[0]
        status = re.search(r'<td class="span2">Status</td>.*?<td>.*?</td>', data).group()
        status = web.striptags(status).strip('Status')
        # Basic user information
        details = data.split('[list]')[1].split('[/list]')[0]
        details = re.sub(r'\<\/.*?\>', '', details)
        details = re.sub(r'\<.*?\>', ' {b}- ', details)
        details = re.sub(r'\[.*?\]', '', details)
        details = details.replace(': ', ': {b}')
        url = 'http://steamcommunity.com/id/' + id
        return code.say('{b}%s{b} - {green}%s{c} - %s - %s' % (realname, status, details, url))
    except:
        if showerror:
            code.say('{b}Unable to find user information on %s!' % id)
        return


@hook(rule=appid_re)
def steam_app_auto(code, input):
    try:
        data = web.get('http://steamdb.info/app/%s/' % web.quote(input.group(1)), timeout=10).read()
        output = []
        output.append(re.findall(r'<td>Name</td><td itemprop="name">(.*?)</td>', data)[0])  # Name
        score = re.findall(r'metacritic_score</td><td>(.*?)</td>', data)  # Metacritic Score
        if len(score) < 1:
            score = '{b}N/A{b}'
        else:
            score = score[0]
        output.append('Rating: %s/100' % score)

        # Released yet?
        if '<td class="span3">releasestate</td><td>prerelease</td>' in data:
            output.append('{blue}Prerelease{c}')

        # OS List
        if '<td class="span3">oslist</td>' in data:
            tmp = re.findall(r'<tr><td class="span3">oslist</td><td>(.*?)</td></tr>', data)[0]
            tmp = re.findall(r'title="(.*?)"', tmp)
            output.append('OS: ' + ', '.join(tmp))
        else:
            output.append('OS: N/A')

        # With pricing, there are a few options...
        # 1. Free, 2. Cost, 3. Cost with discount
        # As well, 1. Not released (May cause issues with rendering the price table) or 2. released

        if 'isfreeapp</td><td>Yes</td>' in data:
            # We know it's free!
            output.append('{green}Free{c}')
        elif '<table class="table table-prices">' in data:
            tmp = re.findall(r'<table class="table table-prices">.*?<tbody><tr>(.*?)</tr></tbody>', data)[0]
            tmp = tmp.replace('<td>', '').split('</td>', 1)[0]
            # We know it's paid... now check if discounted..
            if 'price-discount' in tmp:
                # We know it's discounted
                initial = tmp.split('class="price-initial">', 1)[1].split('</span>', 1)[0]
                new = tmp.split('</span>', 1)[1].split('<', 1)[0]
                discount = tmp.split('"price-discount">', 1)[1].split('<', 1)[0]
                output.append('{green}%s{c} (%s, was %s)' % (new, discount, initial))
            else:
                output.append('{green}' + tmp)

        output.append('http://store.steampowered.com/app/%s/' % re.findall(r'<td class="span3">App ID</td><td>(.*?)</td>', data)[0])
        # if else, it's unknown, so ignore it. Likely an issues with release pricing.
        return str(' - {b}'.join(output).replace(': ', ': {b}'))
    except:
        return
