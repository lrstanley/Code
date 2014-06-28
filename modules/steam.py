from util import web
import re
from util.hook import *

userid_re = r'.*(?:steamcommunity.com|www.steamcommunity.com)/(?:profiles|id)/([-_a-zA-Z0-9]+)/?.*'
# appid_re = r'.*(?:store.steampowered.com|steamcommunity.com|steamdb.info)/app/([0-9]+)/?.*'


@hook(cmds=['steam'], args=True)
def steam_user(code, input):
    """ find user information and worth of a Steam account/username """
    user_lookup(code, input.group(2))


@hook(rule=userid_re)
def steam_user_auto(code, input):
    user_lookup(code, input.group(1), showerror=False)


def user_lookup(code, id, showerror=True):
    try:
        data = web.get('http://steamdb.info/calculator/?player=%s&currency=us' % id).read()
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
        return code.say('{b}%s{b} - {green}%s{c} - %s' % (realname, status, details))
    except:
        if showerror:
            code.say('{b}Unable to find user information on %s!' % id)
        return


# @hook(rule=appid_re)
# def steam_app_auto(code, input):
#     try:
#         data = web.get('http://steamdb.info/app/%s/' % web.quote(input.group(1))).read()
#         name = re.findall(r'<td>Name</td>.*?<td>(.*?)</td>', data)[0]
#         print name
#     except:
#         return
