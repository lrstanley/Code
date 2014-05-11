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
    req = urllib2.Request(uri, headers={'Accept': '*/*', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; Code)'})
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


def pyexec(data, multiline=True):
    attempts = 0

    while True:
        try:
            output = urllib2.urlopen(exec_uri % urllib.quote(data)).read().rstrip('\n')
            # sometimes the API returns a blank string on first attempt, lets try again
            # and make sure it is actually supposed to be a blank string. ._.
            if output == "":
                output = urllib2.urlopen(exec_uri % urllib.quote(data)).read().rstrip('\n')
            break
        except:
            if attempts > 2:
                return "Failed to execute code."
            else:
                attempts += 1
                continue

    if "Traceback (most recent call last):" in output:
        status = "Python error: "
    else:
        status = "Code executed sucessfully: "

    if "\n" in output and multiline:
        return status + haste(output)
    else:
        return output.replace('\n', ' ')


def haste(text, ext='txt'):
    """ pastes text to a hastebin server """
    uri = urllib2.Request(paste_url + '/documents', text)
    page = urllib2.urlopen(uri).read()
    data = loads(page)
    return ("%s/%s.%s" % (paste_url, data['key'], ext))


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
