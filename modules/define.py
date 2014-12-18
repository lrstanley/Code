from util import web
import re
from util.hook import *


uri = 'http://ninjawords.com/definitions/get/{word}'
highlight = [
    'pronoun', 'noun', 'verb', 'adjective', 'adverb',
    'preposition', 'declarative', 'interrogatory',
    'imperative', 'conjugation', 'conjunction', 'declension'
]


@hook(cmds=['define', 'w', 'd'], ex='define example', args=True)
def define(code, input):
    try:
        data = web.json(uri.format(word=web.quote(input.group(2))))[0]
    except:
        return code.reply('{red}Failed to get definition!')

    # Go through filters to remove extra stuff that's not needed.
    word = data['html']
    word = web.striptags(word)
    word = web.escape(word)
    word = word.replace('\\n', '').replace('\n', '')
    while '  ' in word:
        word = word.replace('  ', ' ')

    word = word.encode('ascii', 'ignore')
    if len(word) > 380:
        word = word[:375] + '{c}{b}[...]'

    # loop through and replace all possible type names

    for name in highlight:
        name = ' {} '.format(name)
        if data['query'].lower().strip() == name.lower():
            continue
        tmp = re.findall(name, word, flags=re.IGNORECASE)
        for item in tmp:
            word = word.replace(item, " [{blue}{b}%s{b}{c}] " % item.strip())

    if 'is not in the dictionary.' in word:
        return code.say('Definition for {b}%s{b} not found' % input.group(2))

    name = data['query'][0].upper() + data['query'][1::]
    # Everything below here is for colors only
    word = '{b}{purple}%s{c}{b}: %s' % (name, word[len(data['query']) + 1::])
    word = word.replace('(', '{purple}{b}(').replace(')', '){b}{c}')
    code.say(word)
