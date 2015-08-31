import re
from util import web
from util.hook import *


@hook(cmds=['cyanide'], args=False, rate=5)
def cyanide(code, input):
    """ cyanide -- Pull a random comic from http://explosm.net/ """
    try:
        data = web.text("http://explosm.net/comics/random/")
        img = re.search(r'<meta property="og:image" content="(.*?)">', data).groups(1)[0]
        # Make sure to disable link shortening, as most IRC clients that auto-embed
        # images break if there is a redirect in place.
        code.msg(input.sender, "{img} - Cyanide & Happiness".format(img=img), shorten_urls=False)
    except:
        code.say("{red}Error fetching data from explosm.net.")
