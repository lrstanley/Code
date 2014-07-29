from util import web
import time
import math
from util.hook import *

uri = 'http://www.timeapi.org/%s/now'


@hook(cmds=['t', 'time'], ex='t UTC')
def get_time(code, input):
    """Returns the current time."""
    default = 'est'
    fmt = 'Time in {timezone} is {hour}:{minute}:{second} ({month}/{day}/{year})'
    err = 'Incorrect timezone. Syntax: .time <timezone>'
    if not input.group(2):
        timezone = default
    elif len(input.group(2).split()) > 1:
        timezone = default
    else:
        timezone = input.group(2).lower().strip()

    # Here, try and get the timezone, using the 'uri'
    try:
        r = web.get(uri % timezone).read()

        # Try to parse the string data... this will be fun!
        # Example output from the server... "2014-01-07T09:44:58-05:00"
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
        return code.say(err)


@hook(cmds=['beats'])
def beats(code, input):
    """Shows the internet time in Swatch beats."""
    beats = ((time.time() + 3600) % 86400) / 86.4
    beats = int(math.floor(beats))
    code.say('@%03i' % beats)
