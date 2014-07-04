import re
import urllib2
import HTMLParser
from util.hook import *
from util import web
h = HTMLParser.HTMLParser()

key = '51befff611067'
language = 'en'
mature = False
# http://api.betacie.com/readme.php


@hook(cmds=['fml', 'fmylife'], ex='fml #12390101', rate=15)
def fml(code, input):
    """fml - Retrieve random FML's, via FMyLife.com's dev API."""
    # Random/No input
    if not input.group(2):
        try:
            r = fml_random()
            code.say('#{blue}%s{c} %s +{b}%s{b}/-{b}%s{b}' % (str(r['fml-id']),
                                                              web.htmlescape(r['fml']).replace('FML', '{red}FML{c}'), r['+'], r['-']))
        except:
            return code.say('{red}Failed to retrieve random FML.')
    elif input.group(2).startswith('#') and input.group(2).lstrip('#').isdigit():
        try:
            r = fml_id_search(input.group(2).lstrip('#'))
            code.say('#{blue}%s{c} %s +{b}%s{b}/-{b}%s{b}' % (str(r['fml-id']),
                                                              web.htmlescape(r['fml']).replace('FML', '{red}FML{c}'), r['+'], r['-']))
        except:
            return code.say('Failed to retrieve FML via ID.')
    # Input/Assume search query, with (possible) number at end indicating FML
    # index
    else:
        msg = input.group(2).lower().strip()
        parts = msg.split()
        if parts[-1].replace('-', '').isdigit():
            if int(parts[-1]) <= 0:
                id = 1
            else:
                id = int(parts[-1].replace('-', ''))
            del parts[-1]
            query = '+'.join(parts)
        else:
            id = 1
            query = msg.replace(' ', '+')
        try:
            r = fml_search(query, id)
            code.say(
                '(%s/%s) #{blue}%s{c} %s +{b}%s{b}/-{b}%s{b}' % (r['id'], r['max'], str(r['fml-id']),
                                                                 web.htmlescape(r['fml']).replace('FML', '{red}FML{c}'), r['+'], r['-']))
        except:
            return code.say('Failed to search for FML.')


def fml_random():
    """fml - Retrieve random FML's, via FMyLife.com's dev API."""
    try:
        r = web.get('http://api.fmylife.com/view/random/1?language=%s&key=%s' % (
            language, key
        )).read()
    except:
        return
    fml = re.compile(r'<text>.*?</text>').findall(r)
    fmlid = re.compile(r'<item id=".*?">').findall(r)
    agree = re.compile(r'<agree>.*?</agree>').findall(r)
    deserved = re.compile(r'<deserved>.*?</deserved>').findall(r)
    return {
        'fml': web.htmlescape(web.striptags(fml[0]).strip()),
        'fml-id': fmlid[0].replace('<item id="', '', 1).replace('">', '', 1).strip(),
        '+': web.striptags(agree[0]).strip(),
        '-': web.striptags(deserved[0]).strip()
    }


def fml_search(query, id):  # ID is index of search query
    """fml - Retrieve FML search results, via FMyLife.com's dev API."""
    # Try to query FML
    try:
        query = re.sub(r'[^\w\s]', '+', query)
        query = query.replace('.', '+')
        while query.find('++') > -1:
            query = query.replace('++', '+').strip('+')
        r = web.get(
            'http://api.fmylife.com/view/search?search=%s&language=%s&key=%s' %
            (query, language, key)).read()
    except:
        return
    # find god awful FML
    fml = re.compile(r'<text>.*?</text>').findall(r)
    fmlid = re.compile(r'<item id=".*?">').findall(r)
    count = len(fml)
    if count == 0:
        return code.say('The definition for "{purple}%s{c}" wasn\'t found.' % ' '.join(parts))
    if id > count:
        id = count
    # Who agrees
    agree = re.compile(r'<agree>.*?</agree>').findall(r)
    # It's their fault!
    deserved = re.compile(r'<deserved>.*?</deserved>').findall(r)
    return {
        'fml': web.striptags(fml[id - 1]).strip(),
        'fml-id': fmlid[id - 1].replace('<item id="', '', 1).replace('">', '', 1).strip(),
        '+': web.striptags(agree[id - 1]).strip(),
        '-': web.striptags(deserved[id - 1]).strip(),
        'id': id,
        'max': count
    }


def fml_id_search(query_id):
    """fml - Retrieve the FML in accordance with the assigned ID, via FMyLife.com's dev API."""
    try:
        r = web.get('http://api.fmylife.com/view/%s/nocomment?language=%s&key=%s' % (
            str(query_id),
            language, key
        )).read()
    except:
        return
    fml = re.compile(r'<text>.*?</text>').findall(r)
    fmlid = re.compile(r'<item id=".*?">').findall(r)
    agree = re.compile(r'<agree>.*?</agree>').findall(r)
    deserved = re.compile(r'<deserved>.*?</deserved>').findall(r)
    return {
        'fml': web.htmlescape(web.striptags(fml[0]).strip()),
        'fml-id': fmlid[0].replace('<item id="', '', 1).replace('">', '', 1).strip(),
        '+': web.striptags(agree[0]).strip(),
        '-': web.striptags(deserved[0]).strip()
    }
