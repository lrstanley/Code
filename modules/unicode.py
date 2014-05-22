import re
import time
import unicodedata
import difflib
from util.hook import *
from util.web import get
from util import database
from util import output

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


uc_names, cp_names, uc = [], {}, {}


@hook(cmds=['u'], ex='u SPACE')
def u(code, input, search=False):
    """Look up unicode information."""
    global uc_names, cp_names, uc
    arg = repr(input.group(2)).replace('\u', '').replace('u', '').replace('\'', '')
    if not arg:
        return code.reply('You gave me zero length input.')
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


def gen_db(botname):
    global uc_names, cp_names, uc
    # http://www.unicode.org/reports/tr44/#UnicodeData.txt
    output.info('Downloading Unicode data')
    data = get('http://www.unicode.org/Public/UCD/latest/ucd/UnicodeData.txt').read()
    data = data.split('\n')
    del data[-1]
    # http://www.unicode.org/reports/tr44/#UnicodeData.txt
    for line in data:
        tmp = line.split(';')
        name = tmp[1]
        if tmp[10]:
            name = name + ' ' + str(tmp[10])
        uc[name] = tmp
        uc_names.append(name)
        cp_names[tmp[0]] = name
    database.set(botname, {'uc': uc, 'uc_names': uc_names, 'cp_names': cp_names, 'time': int(time.time())}, 'unicodedata')

def setup(code):
    global uc_names, cp_names, uc
    curr = int(time.time())
    db = database.get(code.nick, 'unicodedata')
    if not db:
        gen_db(code.nick)
    else:
        diff = int(curr - int(db['time']))
        if diff > 518400:
            gen_db(code.nick)
            return
        uc = db['uc']
        uc_names = db['uc_names']
        cp_names = db['cp_names']


@hook(cmds=['us'], ex='us SPACE')
def us(code, input):
    u(code, input, search=True)

def u_converter(string):
    chars = string.split('\u')
    chinese = ''
    for char in chars:
        if len(char):
            try:
                ncode = int(char, 16)
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
