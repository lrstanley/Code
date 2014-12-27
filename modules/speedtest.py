from util import web
from util.hook import *


# http://www.speedtest.net/my-result/<id>
# http://www.speedtest.net/result/<id>.png

uri_regex = r'.*https?://www.speedtest.net/(?:result|my-result)/([0-9]{5,15})(?:\.png)?.*'
uri = 'http://www.speedtest.net/my-result/%s'


@hook(rule=uri_regex, thread=False, supress=True)
def speedtest(code, input):
    id = input.group(1)
    raw = web.clean(web.text(uri % id))
    raw = raw.split('<div class="share-main">', 1)[1]
    raw = raw.split('</div><!--/share-main-->', 1)[0]
    results = web.findin(r'<p>.*?</p>', raw)
    keys = ['Download', 'Upload', 'Ping', 'Device', 'ISP', 'Server']
    tmp = []

    for i in range(0, len(results)-1):
        if len(web.striptags(results[i])) < 1:
            continue
        tmp.append('{b}%s{b}: %s' % (keys[i], web.striptags(results[i])))

    code.say(' {b}-{b} '.join(tmp))
