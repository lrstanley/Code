#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
unicode.py - Code Unicode Module
http://code.liamstanley.io/
"""

import re
import unicodedata
import urlparse
from itertools import islice
from util.hook import *

all_chars = (unichr(i) for i in xrange(0x110000))
control_chars = ''.join(map(unichr, range(0,32) + range(127,160)))
control_char_re = re.compile('[%s]' % re.escape(control_chars))

@hook(cmds=['sc','supercombiner'], rate=30)
def supercombiner(code, input):
    """Displays the infamous supercombiner"""
    s = 'u'
    for i in xrange(1, 3000):
        if unicodedata.category(unichr(i)) == "Mn":
            s += unichr(i)
        if len(s) > 100:
            break
    s = remove_control_chars(s)
    code.say(s)


def decode(bytes):
    try:
        if isinstance(bytes, str) or isinstance(bytes, unicode):
            text = bytes.decode('utf-8')
        else:
            text = str()
    except UnicodeDecodeError:
        try:
            text = bytes.decode('iso-8859-1')
        except UnicodeDecodeError:
            text = bytes.decode('cp1252')
    return text


def encode(bytes):
    try:
        if isinstance(bytes, str) or isinstance(bytes, unicode):
            text = bytes.encode('utf-8')
        else:
            text = str()
    except UnicodeEncodeError:
        try:
            text = bytes.encode('iso-8859-1')
        except UnicodeEncodeError:
            text = bytes.encode('cp1252')
    return text


def urlEncodeNonAscii(b):
    return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)


def iriToUri(iri):
    parts = urlparse.urlparse(iri)
    return urlparse.urlunparse(
        part.encode('idna') if parti == 1 else urlEncodeNonAscii(part.encode('utf-8'))
        for parti, part in enumerate(parts)
    )


def remove_control_chars(s):
    return control_char_re.sub('', s)


def about(u, cp=None, name=None): 
    if cp is None: 
        cp = ord(u)
    if name is None: 
        try: name = unicodedata.name(u)
        except ValueError: 
            return 'U+%04X (No name found)' % cp

    if not unicodedata.combining(u): 
        template = 'U+%04X %s (%s)'
    else:
        template = 'U+%04X %s (\xe2\x97\x8c%s)'
    return template % (cp, name, u.encode('utf-8'))


def codepoint_simple(arg): 
    arg = arg.upper()

    r_label = re.compile('\\b' + arg.replace(' ', '.*\\b') + '\\b')

    results = []
    for cp in xrange(0xFFFF): 
        u = unichr(cp)
        try: name = unicodedata.name(u)
        except ValueError: continue

        if r_label.search(name): 
            results.append((len(name), u, cp, name))
    if not results: 
        r_label = re.compile('\\b' + arg.replace(' ', '.*\\b'))
        for cp in xrange(0xFFFF): 
            u = unichr(cp)
            try: name = unicodedata.name(u)
            except ValueError: continue

            if r_label.search(name): 
                results.append((len(name), u, cp, name))

    if not results: 
        return None

    length, u, cp, name = sorted(results)[0]
    return about(u, cp, name)


def codepoint_extended(arg): 
    arg = arg.upper()
    try: r_search = re.compile(arg)
    except: raise ValueError('Broken regexp: %r' % arg)

    for cp in xrange(1, 0x10FFFF): 
        u = unichr(cp)
        name = unicodedata.name(u, '-')

        if r_search.search(name): 
            yield about(u, cp, name)


@hook(cmds=['u'], ex='u 203D')
def u(code, input): 
    """Look up unicode information."""
    arg = input.bytes[3:]
    if not arg: 
        return code.reply('You gave me zero length input.')
    elif not arg.strip(' '): 
        if len(arg) > 1: return code.reply('%s SPACEs (U+0020)' % len(arg))
        return code.reply('1 SPACE (U+0020)')

    # @@ space
    if set(arg.upper()) - set(
        'ABCDEFGHIJKLMNOPQRSTUVWYXYZ0123456789- .?+*{}[]\\/^$'): 
        printable = False
    elif len(arg) > 1: 
        printable = True
    else: printable = False

    if printable: 
        extended = False
        for c in '.?+*{}[]\\/^$': 
            if c in arg: 
                extended = True
                break

        if len(arg) == 4: 
            try: u = unichr(int(arg, 16))
            except ValueError: pass
            else: return code.say(about(u))

        if extended: 
            # look up a codepoint with regexp
            results = list(islice(codepoint_extended(arg), 4))
            for i, result in enumerate(results): 
                if (i < 2) or ((i == 2) and (len(results) < 4)): 
                    code.say(result)
                elif (i == 2) and (len(results) > 3): 
                    code.say(result + ' [...]')
            if not results: 
                code.reply('Sorry, no results')
        else: 
            # look up a codepoint freely
            result = codepoint_simple(arg)
            if result is not None: 
                code.say(result)
            else: code.reply('{red}Sorry, no results for %r.' % arg)
    else: 
        text = arg.decode('utf-8')
        # look up less than three codepoints
        if len(text) <= 3: 
            for u in text: 
                code.say(about(u))
        # look up more than three codepoints
        elif len(text) <= 10: 
            code.reply(' '.join('U+%04X' % ord(c) for c in text))
        else: code.reply('{red}Sorry, your input is too long!')


@hook(cmds=['bytes'], ex='bytes \xe3\x8b\xa1')
def bytes(code, input): 
    """Show the input as pretty printed bytes."""
    if empty(code, input): return
    b = input.bytes
    code.reply('%r' % b[b.find(' ') + 1:])