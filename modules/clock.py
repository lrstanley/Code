import time
import math
from util import web
from util.hook import *

uri = 'http://www.timeapi.org/{timezone}/now'


@hook(cmds=['t', 'time'], ex='t UTC')
def get_time(code, input):
    """time <abbreviated timezone> -- Returns the current time. Yucky"""
    fmt = 'Time in {timezone} is {hour}:{minute}:{second} ({month}/{day}/{year})'
    if not input.group(2):
        timezone = 'EST'
    elif len(input.group(2).split()) > 1:
        timezone = 'EST'
    else:
        timezone = input.group(2)

    try:
        try:
            r = web.text(uri.format(timezone=timezone.strip().upper()), timeout=15)
        except:
            return code.say('Unable to calculate time for that timezone.')
        date, time = r.split('T')
        year, month, day = date.split('-')[::1]
        hour, minute, second = time.split(':', 2)
        if int(hour) > 12:
            hour = str(int(hour) - 12)
        second = second.split('-', 1)[0].split('+', 1)[0]
        return code.say(fmt.format(
            month=month, day=day, year=year,
            hour=hour, minute=minute, second=second,
            timezone=timezone.upper()
        ))
    except:
        return code.say('Incorrect timezone. Syntax: .time <timezone>')


@hook(cmds=['beats'])
def beats(code, input):
    """beats -- Shows the internet time in Swatch beats."""
    beats = ((time.time() + 3600) % 86400) / 86.4
    beats = int(math.floor(beats))
    code.say('@%03i' % beats)
