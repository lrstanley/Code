import os
import re
from util.hook import *


@hook(rule=r'(?iu)(?:([^\s:,]+)[\s:,])?\s*s\s*([^\s\w])(.*)', priority='high')
def findandreplace(code, input):
    if not input.sender.startswith('#'):
        return

    separator = input.group(2)
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

    if code.chan[input.sender][input.nick]['count'] < 2:
        return

    umsg = list(reversed(code.chan[input.sender][input.nick]['messages']))
    msg_index = None
    for i in range(len(umsg)):
        if umsg[i]['message'].startswith('(me)') or ' s/' in umsg[i]['message'] or umsg[i]['message'].startswith('s/'):
            continue

        new_msg = repl(umsg[i]['message'])
        if new_msg != umsg[i]['message']:  # we are done
            msg_index = i
            break

    if msg_index is None:
        return code.say('{red}Nothing to replace!')
    if not new_msg or new_msg == umsg[msg_index]['message']:
        return

    # Save the new "edited" message.
    # Remember, the above index is reversed so unreverse it.
    new_id = (len(umsg) - 1) - msg_index
    code.chan[input.sender][input.nick][
        'messages'][new_id]['message'] = new_msg
    code.say('%s {b}meant{b} to say: %s' % (input.nick, new_msg))
