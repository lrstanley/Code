from util import web
from util.hook import *


uri = 'http://ninjawords.com/definitions/get/%s'


@hook(cmds=['define', 'w', 'd'], ex='define example', args=True)
def define(code, input):
    try:
        data = web.json(uri % web.quote(input.group(2)))[0]
    except:
        return code.reply('{red}Failed to get definition!')

    # Go through filters to remove extra stuff that's not needed.
    word = data['html']
    word = web.striptags(word).strip()
    word = web.htmlescape(word)
    word = word.replace('\\n', '').replace('\n', '')
    while '  ' in word:
        word = word.replace('  ', ' ')

    word = word.encode('ascii', 'ignore')
    if 'is not in the dictionary.' in word:
        return code.say('Definition for {b}%s{b} not found' % input.group(2))

    # Everything below here is for colors only
    word = '{b}{purple}%s{c}{b}: %s' % (
        data['query'], word[len(data['query']) + 1::])
    word = word.replace('(', '{purple}{b}(').replace(')', '){b}{c}')
    if len(word) > 250:
        word = word[:245] + '{c}{b}[...]'
    code.say(word)
