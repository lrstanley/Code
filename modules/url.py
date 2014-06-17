import re
from util import web
from util.hook import *

url_re = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
title_min_length = 3
url_min_length = 5
ignored = [
    'git.io', 'youtube.', 'youtu.be', 'soundcloud.com', 'imdb.com',
    'ci.liamstanley.io'
]


def get_url_data(url):
    if len(url) < url_min_length:
        return False  # URL is really short. Don't need shortening.
    try:
        uri = web.get(url)
        if not uri.info().maintype == 'text':
            return False
        data = uri.read(1024)  # Only read soo much of a large site.
        title = re.compile('<title>(.*?)</title>',
                           re.IGNORECASE | re.DOTALL).search(data).group(1)
        title = web.htmlescape(title)
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
            output.append('{blue}{b}%s{b}{c} - %s' %
                          (web.uncharset(data), url))
    if not output:
        return
    return code.say(' | '.join(output))
