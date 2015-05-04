from util import web
import time
import re
from util.tools import add_commas
from util.hook import *

yt_regex = r'.*://(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch.+?v=)?([a-zA-Z0-9_-]{5,15}).*'
api_url = 'http://api.liam.sh/?video=%s'
search_url = 'http://ircbot.ml/?youtube=%s&n=%s'


@hook(rule=yt_regex, thread=False, supress=True)
def youtube(code, input):
    """Automatically find the information from a youtube url and display it
       to users in a channel"""
    id = input.group(1)
    if not id:
        return
    id = id.split('&', 1)[0].split(' ', 1)[0].split('#', 1)[0]
    try:
        reply = create_response(web.json(api_url % id), url=False)
    except:
        return
    return code.say(' - '.join(reply))


@hook(cmds=['youtube', 'yt', 'video'], ex='yt PewDiePie 7', rate=10, args=True)
def get_search(code, input):
    """Search youtube for the top video of <query>. Also note, you can specify next response with a number at the end"""
    if input.group(2).strip().split()[-1].isdigit():
        numerical = int(input.group(2).strip().split()[-1])
        if numerical < 1:
            return code.reply('Invalid search number: \'.yt <search query> <#>\'')
    else:
        numerical = 1
    try:
        query = input.group(2).replace(' ', '+')
        data = web.json(search_url % (query, str(numerical)))
        reply = create_response(data, url=True)
        return code.say(' - '.join(reply))
    except:
        return code.reply('{red}Failed to search for %s!' % input.group(2))


def create_response(data, url=False):
    reply = []
    reply.append('{fuchsia}{b}%s{b}{c}' % data['snippet']['title'])
    _len = data['contentDetails']['duration'].lstrip('PT').lower()
    reply.append(re.sub(r'(?P<n>[0-9])', '{b}\g<n>{b}', _len))
    reply.append('{b}+%s{b}/{b}-%s{b} likes' % (add_commas(data['statistics']['likeCount']), add_commas(data['statistics']['dislikeCount'])))
    reply.append('{b}%s{b} views' % add_commas(data['statistics']['viewCount']))
    upload_time = parse_date(data['snippet']['publishedAt'])
    reply.append('by {fuchsia}{b}%s{b}{c} on {b}%s{b}' % (data['snippet']['channelTitle'], upload_time))

    if 'contentRating' in data['contentDetails']:
        reply.append('{red}{b}NSFW{b}{red}')
    if url:
        reply.append('https://www.youtube.com/watch?v=' + data['id'])
    return reply


def parse_date(thedate):
    upload_time = time.strptime(thedate, '%Y-%m-%dT%H:%M:%S.000Z')
    return time.strftime("%m/%d/%Y", upload_time)
