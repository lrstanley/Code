import re
from util import web
from util.hook import *
from util.tools import compare


url_re = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
title_min_length = 3
url_min_length = 5
ignored = [
    'git.io', 'youtube.', 'youtu.be', 'soundcloud.com', 'imdb.com',
    'zerobin.net', 'newegg.com', 'steamcommunity.com', 'speedtest.net',
    'steampowered.com', 'steamdb.info', 'links.ml', 'twitter.com',
    'github.com'
]

safe_mime = ['text']
safe_status_codes = [200, 201, 202, 203, 204, 206, 301, 302, 304, 307, 308]


def get_url_data(url):
    if len(url) < url_min_length:
        return False  # URL is really short. Don't need shortening.
    try:
        # Pull the headers and content, before we actually pull the data. Test HTTP status codes,
        # as well as force redirection (not enabled by default for HEAD requests)
        test = web.head(url, allow_redirects=True, verify=False)
        if test.headers['content-type'].split('/', 1)[0].lower() not in safe_mime:
            return False
        if test.status_code not in safe_status_codes:
            return False
        uri = web.get(url, verify=False)
        if not uri.text:
            return False
        title = re.compile('<title>(.*?)</title>', re.IGNORECASE | re.DOTALL).search(uri.text).group(1)
        title = web.escape(title)
        title = title.replace('\n', '').replace('\r', '')

        # Remove spaces...
        while '  ' in title:
            title = title.replace('  ', ' ')

        if compare(title, url.split('//', 1)[1], advanced=True) > 100:
            # Return if it's very similar to eachother (they're using pretty urls, which show
            # title words in the url)
            return False
        # Shorten LONG urls
        if len(title) > 200:
            title = title[:200] + '[...]'

        if len(title) < title_min_length:  # Title output too short
            return False

        return title
    except:
        return False


@hook(rule=r'(?i).*%s.*' % url_re, priority='high')
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
