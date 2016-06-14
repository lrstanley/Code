import re
from util.hook import *
from util import web

key = '51befff611067'
language = 'en'
mature = False
uri = 'http://api.fmylife.com/view%s'
# API docs: http://api.betacie.com/readme.php


@hook(cmds=['fml', 'fmylife'], ex='fml #12390101', rate=15)
def fml(code, input):
    """fml - Retrieve random FML's from fmylife.com."""
    # Random/No input
    if not input.group(2):
        f = fml_fetch(random=True)
        if not f:
            return code.say('{red}Failed to retrieve random FML.')

        return code.say('#{blue}%(id)d{c} %(fml)s +{b}%(agree)d{b}/-{b}%(deserved)d{b} - http://fmylife.com/%(id)d' % f)

    elif input.group(2).startswith('#') and input.group(2).lstrip('#').isdigit():
        f = fml_fetch(by_id=input.group(2).lstrip('#'))
        if not f:
            return code.say('Failed to retrieve FML via ID.')

        return code.say('#{blue}%(id)d{c} %(fml)s +{b}%(agree)d{b}/-{b}%(deserved)d{b} - http://fmylife.com/%(id)d' % f)

    # Input/Assume search query, with (possible) number at end indicating FML
    # index
    else:
        msg = input.group(2).lower().strip()
        parts = msg.split()
        if parts[-1].isdigit():
            id = int(parts[-1])

            del parts[-1]
            query = '+'.join(parts)
        else:
            id = 1
            query = msg.replace(' ', '+')

        f = fml_fetch(search=(query, id))
        if not f:
            return code.say('Failed to search for FML.')

        return code.say('(%(uid)d/%(max)d) #{blue}%(id)d{c} %(fml)s +{b}%(agree)d{b}/-{b}%(deserved)d{b} - http://fmylife.com/%(id)d' % f)


def fml_fetch(random=False, by_id=False, search=False):
    if not random and not by_id and not search:
        raise ValueError

    args = {
        "language": language,
        "key": key
    }

    try:
        if random:
            return fml_fmt(web.text(uri % '/random/1', params=args))
        elif by_id:
            return fml_fmt(web.text(uri % '/{0}/nocomment'.format(str(by_id)), params=args))
        elif search:
            # search should be a tuple of (query, id) pair
            args['search'] = search[0]
            return fml_fmt(web.text(uri % '/search', params=args), id=search[1])
    except:
        return False


def fml_fmt(data, id=0):
    raw_items = [item for item in re.compile(r'<item .*?>.*?</item>').findall(data)]

    if not raw_items:
        return False

    items, count = [], 0
    for f in raw_items:
        count += 1
        try:
            items.append({
                'fml': web.escape(web.striptags(re.compile(r'<text>(.*?)</text>').findall(f)[0])).replace('FML', '{red}FML{c}'),
                'id': int(re.compile(r'<item .*id="([0-9]+)".*>').findall(f)[0]),
                'uid': count,
                'max': len(raw_items),
                'agree': int(web.striptags(re.compile(r'<agree>(.*?)</agree>').findall(f)[0])),
                'deserved': int(web.striptags(re.compile(r'<deserved>(.*?)</deserved>').findall(f)[0]))
            })

        except:
            items.append(False)

    if id < 1:
        id = 1
    if id > len(raw_items):
        id = len(raw_items)
    id = id - 1

    return items[id]
