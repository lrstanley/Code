import re
from util import web
from util.hook import *


@hook(cmds=['xkcd'], args=False, rate=5)
def xkcd(code, input):
    """ xkcd -- Pull a random comic from http://xkcd.com/ """
    try:
        data = web.text("http://c.xkcd.com/random/comic/")
        comic = re.search(r'<img src="(.*?)" title="(.*?)" alt="(.*?)" />', data).groups()
        # Make sure to disable link shortening, as most IRC clients that auto-embed
        # images break if there is a redirect in place.
        code.msg(input.sender, "{desc} - http:{img} - xkcd".format(desc=web.decode(comic[1]), img=comic[0]), shorten_urls=False)
    except:
        code.say("{red}Error fetching data from xkcd.com")
