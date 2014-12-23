import re
from util import web
from util.hook import *
from util import output

uri = 'http://duckduckgo.com/html/'
# Ensure both url_count and url_colors are the same length
url_count = 3
url_colors = ['blue', 'green', 'teal']
title_length = 50


@hook(cmds=['search', 'google', 'g', 'ddg', 'duckduckgo'], ex='search Twitter API', rate=10, args=True)
def search(code, input):
    """Queries DuckDuckGo for the specified input."""

    try:
        data = web.get(uri, params={'q': input.group(2)})
        tmp = data.text.replace('\r', '').replace('\n', '').strip()
        target = r'(?im)<div class="results_links .*?(?!.*web\-result\-sponsored)">.*?<a .*? href="(.*?)">.*?</a>.*?' \
            '<div class="snippet">(.*?)</div>.*?<div class="url">(.*?)</div>'
        found = list(re.findall(target, tmp))
        if len(found) > url_count:
            found = found[:url_count]
        results = []
        if len(found) < 2:
            return code.say('{b}No results found{b}')
        count = 0
        for item in found:
            i = list(item)
            result = {}
            result['url'] = web.escape(web.striptags(i[0]))
            result['short'] = web.escape(web.striptags(i[2]).capitalize().split('/')[0])
            result['title'] = web.escape(web.striptags(i[1]))
            if len(result['title']) > title_length:
                result['title'] = result['title'][:title_length] + '{b}...{b}'

            results.append('{b}%s{b} - {%s}%s{c} - %s' % (result['short'], url_colors[count], result['title'], result['url']))
            count += 1
        return code.say(' | '.join(results))
    except Exception as e:
        output.error('Error in search.py: %s' % str(e))
        return code.say('{b}Unable to search for %s{b}' % input.group(2))
