import json
import urllib2
import HTMLParser
from util.hook import *
h = HTMLParser.HTMLParser()


@hook(cmds=['chuck', 'cn'], rate=10)
def chuck(code, input):
    """Get random Chuck Norris facts. I bet he's better than you. :P"""
    try:
        r = urllib2.urlopen('http://api.icndb.com/jokes/random').read()
    except:
        return code.say('Chuck seems to be in the way. I\'m not fucking with him.')
    data = json.loads(r)
    code.say('#{blue}%s{c} - %s' % (data['value']['id'], h.unescape(data['value']['joke'])))
