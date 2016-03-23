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
        target = r'(?im)(<div class="result results_links.*?">.*?<a .*?class="result__a" href="([^"]+)">(.*?)</a>.*?</div>)'
        found = [x for x in list(re.findall(target, tmp)) if len(x) > 0 and "badge--ad" not in x[0]]
        if len(found) > url_count:
            found = found[:url_count]
        results = []
        if len(found) < 1:
            return code.say('{b}No results found{b}')

        count = 0
        for item in found:
            i = list(item)
            result = {}
            result['url'] = i[1]
            result['title'] = web.escape(web.striptags(i[2]))

            if len(result['title']) > title_length:
                result['title'] = result['title'][:title_length] + '{b}...{b}'

            results.append('{%s}%s{c} - %s' % (url_colors[count], result['title'], result['url']))
            count += 1

        return code.say(' | '.join(results))

    except Exception as e:
        output.error('Error in search.py: %s' % str(e))
        return code.say('{b}Unable to search for %s{b}' % input.group(2))
