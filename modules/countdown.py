import datetime
from util.hook import *


@hook(cmds=['countdown'], priority='low', args=True)
def countdown(code, input):
    """ .countdown <month> <day> <year> - displays a countdown to a given date. """
    error = '{red}Please use correct format: %scountdown <month> <day> <year>' % code.prefix
    text = input.group(2).strip()
    if ' ' in text:
        text = text.split()
    elif '/' in text:
        text = text.split('/')
    elif '.' in text:
        text = text.split('.')
    else:
        return code.say(error)
    if len(text) != 3:
        return code.say(error)
    if not text[0].isdigit() or not text[1].isdigit() or not text[2].isdigit():
        return code.say(error)
    month, day, year = text
    try:
        diff = datetime.datetime(
            int(year), int(month), int(day)) - datetime.datetime.today()
    except ValueError:
        return code.say('{red}Incorrect input!')
    output = []
    output.append(str(diff.days) + " day(s)")
    output.append(str(diff.seconds / 60 / 60) + " hour(s)")
    output.append(
        str(diff.seconds / 60 - diff.seconds / 60 / 60 * 60) + " minute(s)")
    output.append(month + "/" + day + "/" + year)
    code.say(' - '.join(output))
