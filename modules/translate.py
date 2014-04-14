import json
import urllib
import urllib2
import util.web
from util.hook import *


def translate(text, input='auto', output='en'):
    raw = False
    if output.endswith('-raw'):
        output = output[:-4]
        raw = True

    opener = urllib2.build_opener()
    opener.addheaders = [(
        'User-Agent', 'Mozilla/5.0' +
        '(X11; U; Linux i686)' +
        'Gecko/20071127 Firefox/2.0.0.11'
    )]

    input, output = urllib.quote(input), urllib.quote(output)
    text = urllib.quote(text)

    uri = 'https://translate.google.com/translate_a/t?'
    params = {
        'sl': input,
        'tl': output,
        'js': 'n',
        'prev': '_t',
        'hl': 'en',
        'ie': 'UTF-8',
        'text': text,
        'client': 't',
        'multires': '1',
        'sc': '1',
        'uptl': 'en',
        'tsel': '0',
        'ssel': '0',
        'otf': '1',
    }

    for x in params:
        uri += '&%s=%s' % (x, params[x])

    result = opener.open(uri).read()

    # this is hackish
    # this makes the returned data parsable by the json module
    result = result.replace(',,', ',').replace('[,', '["",')

    while ',,' in result:
        result = result.replace(',,', ',null,')
    data = json.loads(result)

    if raw:
        return str(data), 'en-raw'

    try:
        language = data[2]
    except:
        language = '?'

    if isinstance(language, list):
        language = data[-2][0][0]

    return ''.join(x[0] for x in data[0]), language


@hook(cmds=['tr', 'translate'], args=True)
def tr(code, input):
    """Translates a phrase, with an optional language hint."""
    command = input.group(2).encode('utf-8')

    def langcode(p):
        return p.startswith(':') and (2 < len(p) < 10) and p[1:].isalpha()

    args = ['auto', 'en']

    for i in xrange(2):
        if ' ' not in command:
            break
        prefix, cmd = command.split(' ', 1)
        if langcode(prefix):
            args[i] = prefix[1:]
            command = cmd
    phrase = command

    if (len(phrase) > 350) and (not input.admin):
        return code.say('{red}Phrase must be under 350 characters.')

    src, dest = args
    if src != dest:
        msg, src = translate(phrase, src, dest)
        if isinstance(msg, str):
            msg = msg.decode('utf-8')
        if msg:
            msg = util.web.decode(msg)
            msg = '"%s" ({b}{purple}%s{c}{b} to {b}{purple}%s{c}{b})' % (msg, src, dest)
        else:
            msg = '{red}The %s to %s translation failed, sorry!' % (src, dest)

        code.reply(msg)
    else:
        code.say('{red}Language guessing failed, so try suggesting one!')
