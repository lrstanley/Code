import re
from urllib import quote
from urllib2 import urlopen
from util.hook import *


uri = 'http://en.wiktionary.org/w/index.php?title=%s&printable=yes'
r_tag = re.compile(r'<[^>]+>')
r_ul = re.compile(r'(?ims)<ul>.*?</ul>')
parts = (
    'preposition', 'particle', 'blue', 'noun', 'verb',
    'adjective', 'adverb', 'interjection'
)


def text(html):
    text = r_tag.sub('', html).strip()
    text = text.replace('\n', ' ')
    text = text.replace('\r', '')
    text = text.replace('(intransitive', '(intr.')
    text = text.replace('(transitive', '(trans.')
    return text


def wiktionary(word):
    try:
        bytes = urlopen(uri % quote(word.encode('utf-8'))).read()
    except:
        return False, False
    bytes = r_ul.sub('', bytes)

    mode = None
    etymology = None
    definitions = {}
    for line in bytes.splitlines():
        if 'id="Etymology"' in line:
            mode = 'etymology'
        elif 'id="Noun"' in line:
            mode = 'noun'
        elif 'id="Verb"' in line:
            mode = 'verb'
        elif 'id="Adjective"' in line:
            mode = 'adjective'
        elif 'id="Adverb"' in line:
            mode = 'adverb'
        elif 'id="Interjection"' in line:
            mode = 'interjection'
        elif 'id="Particle"' in line:
            mode = 'particle'
        elif 'id="Preposition"' in line:
            mode = 'preposition'
        elif 'id="' in line:
            mode = None

        elif (mode == 'etmyology') and ('<p>' in line):
            etymology = text(line)
        elif (mode is not None) and ('<li>' in line):
            definitions.setdefault(mode, []).append(text(line))

        if '<hr' in line:
            break
    return etymology, definitions


def format(word, definitions, number=2):
    result = '{purple}{b}%s{b}{c}' % word.encode('utf-8')
    for part in parts:
        if part in definitions:
            defs = definitions[part][:number]
            result += u' \u2014 ' + ('{blue}{b}%s{c}{b}: ' % part)
            n = ['%s. %s' % (i + 1, e.strip(' .')) for i, e in enumerate(defs)]
            result += ', '.join(n)
    return result.strip(' .,')


@hook(cmds=['w', 'define', 'd'], ex='w example', args=True)
def w(code, input):
    word = input.group(2).lower()
    etymology, definitions = wiktionary(word)
    if not definitions:
        code.say('{red}Couldn\'t get any definitions for {b}%s{b}.' % word)
        return

    result = format(word, definitions)
    if len(result) < 150:
        result = format(word, definitions, 3)

    if len(result) > 300:
        result = result[:294] + ' [...]'
    code.say(result)
