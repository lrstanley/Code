import re
import urllib
import urllib2
from lib import requests
from htmlentitydefs import name2codepoint
from util.tools import remove_spaces
import HTMLParser
h = HTMLParser.HTMLParser()


paste_url = 'http://paste.ml'
short_ignored = ['bit.ly', 'is.gd', 'goo.gl', 'links.ml']
exec_uri = 'http://eval.appspot.com/eval'


def http(method, rdata='all', uri=None, timeout=7, params=None, data=None, headers=None, **kwargs):
    if not method:
        raise 'No method specified'
    if not uri:
        raise 'Invalid URI supplied'
    if not headers:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.4 (KHTML, '
                          'like Gecko) Chrome/22.0.1229.79 Safari/537.4',
            'Cache-Control': 'max-age=0',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'X-Service': 'Code Python IRC Bot'
        }
    if method == 'get':
        response = requests.get(uri, timeout=timeout, params=params, headers=headers, **kwargs)
    elif method == 'post':
        response = requests.post(uri, timeout=timeout, data=data, headers=headers, **kwargs)
    elif method == 'head':
        response = requests.head(uri, timeout=timeout, data=data, headers=headers, **kwargs)
    else:
        raise 'Method not supported'

    if rdata == 'all':
        return response
    elif rdata == 'json':
        return response.json()
    elif rdata == 'text':
        return response.text
    elif rdata == 'headers':
        return response.headers
    else:
        raise 'Return data not supported'


def post(uri, **args):
    return http(method='post', rdata='all', uri=uri, **args)


def get(uri, **args):
    return http(method='get', rdata='all', uri=uri, **args)


def json(uri, **args):
    return http(method='get', rdata='json', uri=uri, **args)


def text(uri, **args):
    return http(method='get', rdata='text', uri=uri, **args)


def headers(uri, **args):
    return http(method='get', rdata='headers', uri=uri, **args)


def head(uri, **args):
    return http(method='head', rdata='all', uri=uri, **args)


def quote(string):
    return urllib2.quote(string)


def urlencode(data):
    return urllib.urlencode(data)


r_entity = re.compile(r'&([^;\s]+);')


def findin(regex, string, least=1):
    tmp = list(re.findall('(?m)' + regex, string))
    if len(tmp) < 1:
        raise Exception('No results found')
    return tmp


def entity(match):
    value = match.group(1).lower()
    if value.startswith('#x'):
        return unichr(int(value[2:], 16))
    elif value.startswith('#'):
        return unichr(int(value[1:]))
    elif value in name2codepoint:
        return unichr(name2codepoint[value])
    return '[' + value + ']'


def escape(string):
    return h.unescape(string)


def striptags(string):
    return re.compile(r'(?ims)<[^>]+>').sub('', string).strip()


def clean(string):
    string = string.replace('\r', '').replace('\n', '')
    return remove_spaces(escape(string)).strip()


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


def haste(string, extension='txt'):
    data = post(paste_url + '/documents', data=string).json()
    return '{uri}/{key}.{ext}'.format(uri=paste_url, key=data['key'], ext=extension)


def shorten(url):
    try:
        for bad in short_ignored:
            if bad in url.lower():
                return url
        data = post('http://links.ml/add', data={'url': url}).json()
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
            data = text(exec_uri, params={"statement": data}).strip('\n')
            if len(data) == 0:
                continue
            break
        except:
            continue
    return data
