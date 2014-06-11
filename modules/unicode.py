import re
import unicodedata
from util.hook import *

all_chars = (unichr(i) for i in xrange(0x110000))
control_chars = ''.join(map(unichr, range(0, 32) + range(127, 160)))
control_char_re = re.compile('[%s]' % re.escape(control_chars))


@hook(cmds=['sc', 'supercombiner'], rate=30)
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


def remove_control_chars(s):
    return control_char_re.sub('', s)


@hook(cmds=['bytes'], ex='bytes \\xe3\\x8b\\xa1', args=True)
def bytes(code, input):
    """Show the input as pretty printed bytes."""
    b = input.bytes
    code.reply('%r' % b[b.find(' ') + 1:])
