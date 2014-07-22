import re
import urllib
import urllib2
from json import loads
from htmlentitydefs import name2codepoint
import HTMLParser
h = HTMLParser.HTMLParser()


paste_url = 'http://paste.ml'
short_ignored = ['bit.ly', 'is.gd', 'goo.gl', 'links.ml']
exec_uri = 'http://eval.appspot.com/eval?statement=%s'


def get(uri, timeout=5):
    uri = uri.encode("utf-8")
    req = urllib2.Request(uri, headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.4 (KHTML, '
        'like Gecko) Chrome/22.0.1229.79 Safari/537.4'})
    try:
        u = urllib2.urlopen(req, None, timeout)
    except urllib2.HTTPError, e:
        return e.fp
    except:
        raise
    return u


def json(uri, timeout=5):
    try:
        data = get(uri, timeout).read()
        if data[0] == '[' and data[-1] == ']':
            data = '{"json": %s}' % data
            data = loads(data)['json']
        else:
            data = loads(data)
    except urllib2.HTTPError, e:
        return e.fp
    except:
        raise
    return data


def quote(string):
    return urllib2.quote(string)


def urlencode(data):
    return urllib.urlencode(data)


def head(uri):
    if not uri.startswith('http'):
        return
    u = urllib.urlopen(uri)
    info = u.info()
    u.close()
    return info


def post(uri, query):
    if not uri.startswith('http'):
        return
    data = urllib.urlencode(query)
    u = urllib.urlopen(uri, data)
    bytes = u.read()
    u.close()
    return bytes

r_entity = re.compile(r'&([^;\s]+);')


def entity(match):
    value = match.group(1).lower()
    if value.startswith('#x'):
        return unichr(int(value[2:], 16))
    elif value.startswith('#'):
        return unichr(int(value[1:]))
    elif value in name2codepoint:
        return unichr(name2codepoint[value])
    return '[' + value + ']'


def htmlescape(message):
    return h.unescape(message)


def striptags(message):
    return re.compile(r'(?ims)<[^>]+>').sub('', message)


def decode(html):
    return r_entity.sub(entity, html)


def uncharset(string):
    try:
        string = unicode(string, 'utf-8')
    except:
        pass
    try:
        string = string.encode('utf8', 'ignore')
    except:
        pass
    try:
        string = unicode(string, 'utf-8')
    except:
        pass
    return string


r_string = re.compile(r'("(\\.|[^"\\])*")')
r_json = re.compile(r'^[,:{}\[\]0-9.\-+Eaeflnr-u \n\r\t]+$')
env = {'__builtins__': None, 'null': None, 'true': True, 'false': False}


def haste(text, extension='txt'):
    uri = urllib2.Request(paste_url + '/documents', text)
    page = urllib2.urlopen(uri).read()
    data = loads(page)
    return '%s/%s.%s' % (paste_url, data['key'], extension)


def shorten(url):
    try:
        for bad in short_ignored:
            if bad in url.lower():
                return url
        postdata = urllib.urlencode({url: ''})
        data = loads(urllib2.urlopen('http://links.ml/add', postdata).read())
        if not data['success']:
            return url
        return data['url']
    except:
        return url


def exec_py(data):
    attempts = 0
    while True:
        if attempts == 2:
            return "Failed to execute code."
        attempts += 1
        try:
            output = get(exec_uri % quote(data)).read().strip('\n')
            if len(output) == 0:
                continue
            break
        except:
            continue
    return output
