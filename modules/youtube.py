import re
from util import web
import time
from util.tools import add_commas
from util.hook import *

yt_regex = r'.*https?://(www\.)?(youtube\.com|youtu\.be)\/watch.+?v=(.*\w?).*?'
api_url = 'http://gdata.youtube.com/feeds/api/videos/%s?v=2&alt=jsonc'
search_url = 'http://gdata.youtube.com/feeds/api/videos?max-results=1&v=2&alt=jsonc&start-index=%s&q=%s'


@hook(rule=yt_regex, thread=False)
def youtube(code, input):
    """Automatically find the information from a youtube url and display it
       to users in a channel"""
    try:
        id = list(re.findall(yt_regex, str(input.group())))
        if not id:
            return
        id = id[0][2].split('&', 1)[0].split(' ', 1)[0].split('#', 1)[0]
        data = web.json(api_url % id)['data']

        # Set some variables, because we'll have to modify a vew before we spit
        # them back out!
        reply = create_response(data, url=False)
        return code.say(' - '.join(reply))
    except:
        return


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
        data = web.json(search_url % (str(numerical), query))['data']
        reply = create_response(data['items'][0], url=True)
        return code.say(' - '.join(reply))
    except:
        return code.reply('{red}Failed to search for %s!' % input.group(2))


def create_response(data, url=False):
    reply = []
    # Should surely have a title, but just in case :P
    if 'title' in data:
        reply.append('{fuchsia}{b}%s{b}{c}' % data['title'])
    # Some length data ;)
    if 'duration' in data:
        length = data['duration']
        lenout = ''
        if length / 3600:  # > 1 hour
            lenout += '%dh ' % (length / 3600)
        if length / 60:
            lenout += '%dm ' % (length / 60 % 60)
            lenout += "%ds" % (length % 60)
        reply.append('{b}length{b} %s' % lenout)
    # Shitty video? FIND OUT!
    if 'rating' in data and 'ratingCount' in data:
        reply.append('{b}rated{b} %.2f/5.00 (%s)' % (
            data['rating'], add_commas(data['ratingCount'])
        ))
    # Number of views. Yuck.
    if 'viewCount' in data:
        reply.append('%s {b}views{b}' % add_commas(data['viewCount']))
    upload_time = parse_date(data['uploaded'])
    reply.append('by {fuchsia}{b}%s{b}{c} on {b}%s{b}' %
                 (data['uploader'], upload_time))
    # Dis shit not be child appr0ved
    if 'contentRating' in data:
        reply.append('{red}{b}NSFW{b}{red}')
    if url and data['player']['default']:
        url = data['player']['default'].split('&', 1)[0].strip()
        reply.append(url)
    return reply


def parse_date(thedate):
    upload_time = time.strptime(thedate, '%Y-%m-%dT%H:%M:%S.000Z')
    return time.strftime("%Y.%m.%d", upload_time)
