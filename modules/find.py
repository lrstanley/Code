import re
from util.hook import *
from util.tools import hrt
import time


@hook(rule=r'(?iu)^s(?:\/)(.*?)(?:\/)(.*?)(?:(?:\/)(.*?)|(?:\/))?$', priority='high')
def findandreplace(code, input):
    if not input.sender.startswith('#'):
        return

    target, replacement, flags = input.groups()
    if flags != None:
        flags = flags.strip()
    else:
        flags = ""

    # Replace unlimited times if /g flag, else once
    count = 'g' in flags and -1 or 1

    if 'i' in flags:
        regex = re.compile(re.escape(target), re.U | re.I)
        repl = lambda s: re.sub(regex, '{b}' + replacement + '{b}', s, count == 1)
    else:
        repl = lambda s: s.replace(target, '{b}' + replacement + '{b}', count)

    channel_messages = list(reversed(code.logs['channel'][input.sender]))
    msg_index = None
    for i in range(len(channel_messages)):
        if channel_messages[i]['message'].startswith('(me)') or \
        ' s/' in channel_messages[i]['message'].lower() or \
        channel_messages[i]['message'].lower().startswith('s/') or \
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
