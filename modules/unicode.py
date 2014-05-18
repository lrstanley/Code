import re
import unicodedata
import difflib
from util.hook import *
from util.web import get

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


@hook(cmds=['u'], ex='u 203D')
def u(code, input, search=False):
    """Look up unicode information."""
    arg = input.bytes[3:]
    if not arg:
        return code.reply('You gave me zero length input.')
    data = get('http://www.unicode.org/Public/UCD/latest/ucd/UnicodeData.txt').read()
    data = data.split('\n')
    del data[-1]
    uc = {}
    uc_names, cp_names = [], {}
    # http://www.unicode.org/reports/tr44/#UnicodeData.txt
    for line in data:
        tmp = line.split(';')
        name = tmp[1]
        if tmp[10]:
            name = name + ' ' + str(tmp[10])
        uc[name] = tmp
        uc_names.append(name)
        cp_names[tmp[0]] = name

    found = difflib.get_close_matches(arg, uc_names)
    if not found:
        found = difflib.get_close_matches(arg.upper(), uc_names)
    if found:
        if search:
            return code.say('{b}Possible matches:{b} %s' % ', '.join(found))
        char = uc[list(found)[0]]
    if not found:
        # Try the codepoint search too...
        if arg.upper() in cp_names:
            char = uc[cp_names[arg.upper()]]
        else:
            return code.reply('I can\'t seem to find that Unicode!')
    msg = u'{} (U+{}) '.format(char[1], char[0])
    msg += '"' + u_converter('\u' + char[0]) + '"'
    code.say(msg)


@hook(cmds=['ul'], ex='u SPACE')
def ul(code, input):
    u(code, input, search=True)

def u_converter(string):
    chars = string.split('\u')
    chinese = ''
    for char in chars:
        if len(char):
            try:
                ncode = int(char,16)
            except ValueError:
                continue
            try:
                uchar = unichr(ncode)
            except ValueError:
                continue
            chinese += uchar
    return chinese


@hook(cmds=['bytes'], ex='bytes \xe3\x8b\xa1', args=True)
def bytes(code, input):
    """Show the input as pretty printed bytes."""
    b = input.bytes
    code.reply('%r' % b[b.find(' ') + 1:])
