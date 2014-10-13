import re
from util.hook import *
from util.tools import hrt
import time


@hook(rule=r'(?iu)(?:([^\s:,]+)[\s:,])?\s*s\s*([^\s\w])(.*)$', priority='high')
def findandreplace(code, input):
    if not input.sender.startswith('#'):
        return

    separator = input.group(2)
    #if not separator.lower().startswith('s/'):
    #    return
    line = input.group(3).split(separator)
    flags = ''

    if len(line) < 2 or len(line[0]) < 1:
        return

    if len(line) >= 3:
        # Word characters immediately after the second separator
        #   are considered flags (only g and i now have meaning)
        flags = re.match(r'\w*', line[2], re.U).group(0)

    # Replace unlimited times if /g, else once
    count = 'g' in flags and -1 or 1

    if 'i' in flags:
        regex = re.compile(re.escape(line[0]), re.U | re.I)
        repl = lambda s: re.sub(regex, '{b}' + line[1] + '{b}', s, count == 1)
    else:
        repl = lambda s: s.replace(line[0], '{b}' + line[1] + '{b}', count)

    channel_messages = list(reversed(code.logs['channel'][input.sender]))
    msg_index = None
    for i in range(len(channel_messages)):
        if channel_messages[i]['message'].startswith('(me)') or \
        ' s/' in channel_messages[i]['message'] or \
        channel_messages[i]['message'].startswith('s/') or \
        channel_messages[i]['nick'] == code.nick:
            continue

        new_msg = repl(channel_messages[i]['message'])
        if new_msg != channel_messages[i]['message']:  # we are done
            msg_index = i
            break

    if msg_index is None:
        return code.say('{red}Nothing to replace!')
    if not new_msg or new_msg == channel_messages[msg_index]['message']:
        return

    # Save the new "edited" message.
    # Remember, the above index is reversed so unreverse it.
    new_id = (len(channel_messages) - 1) - msg_index
    code.logs['channel'][input.sender][new_id]['message'] = new_msg
    info = code.logs['channel'][input.sender][new_id]
    code.say('({b}%s{b} ago) <{b}%s{b}> %s' % (hrt(info['time'])[0], info['nick'], info['message']))
