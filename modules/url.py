import re
from util import web
from util.hook import *

url_re = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
title_min_length = 3
url_min_length = 5
ignored = [
    'git.io', 'youtube.', 'youtu.be', 'soundcloud.com', 'imdb.com',
    'ci.liamstanley.io', 'zerobin.net', 'newegg.com', 'steamcommunity.com',
    'steampowered.com', 'steamdb.info', 'links.ml', 'twitter.com',
    'github.com'
]


def get_url_data(url):
    if len(url) < url_min_length:
        return False  # URL is really short. Don't need shortening.
    try:
        uri = web.get(url, verify=False)
        if not uri.text:
            return False
        title = re.compile('<title>(.*?)</title>',
                           re.IGNORECASE | re.DOTALL).search(uri.text).group(1)
        title = web.escape(title)
        title = title.replace('\n', '').replace('\r', '')

        # Remove spaces...
        while '  ' in title:
            title = title.replace('  ', ' ')

        # Shorten LONG urls
        if len(title) > 200:
            title = title[:200] + '[...]'

        if len(title) < title_min_length:  # Title output too short
            return False

        return title
    except:
        return False


@hook(rule='(?i).*%s.*' % url_re, priority='high')
def get_title_auto(code, input):
    if input.startswith(code.prefix) or input.startswith('?'):
        return  # Prevent triggering of other plugins
    urls = re.findall('(?i)' + url_re, input)
    # If a user wants to spam... lets limit is to 3 URLs max, per line
    if len(urls) > 3:
        urls = urls[0:3]
    output = []
    for url in urls:
        # check to see if we should ignore this URL...
        if '.' not in url:
            break
        if url.startswith('.') or url.endswith('.'):
            break
        for bad in ignored:
            if bad.lower() in url.lower():
                skip = True
                break
            else:
                skip = False
        if skip:
            break
        # Lets get some data!
        data = get_url_data(url)
        if data:
            if not re.search(r'(?i)page not found', data):
                output.append('{blue}{b}%s{b}{c} - %s' % (data, url))
    if not output:
        return
    return code.say(' | '.join(output))
