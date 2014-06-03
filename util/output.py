import sys
import platform
from tools import split_len

colors = True
parse = True

# Note: Background would be 4#
black, red, green, yellow, blue, magenta, cyan, white = range(8)
colors = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
raw_color, reset, bold = "\x1b[3%dm", "\033[0m", "\033[1m"
pad = 12
split_at = 60


def format_colors(message):
    colorcodes, count = {}, 0
    for i in range(8):
        colorcodes[colors[count].lower()] = i
        count += 1
    if platform.system().lower() != 'windows' or not colors:
        message = message.replace('$reset', reset).replace('$bold', bold)
        for color in colors:
            message = message.replace('$' + color, raw_color % colorcodes[color])
    else:
        message = message.replace('$reset', '').replace('$bold', '')
        for color in colors:
            message = message.replace('$' + color, '')
    return message


def template(message, prefix, color, error=False):
    if not prefix:
        prefix = ''
    message, prefix, color = str(message), str(prefix), str(color)
    if not parse:
        if error:
            print >> sys.stderr, '[%s] %s' % (prefix, message)
        else:
            print >> sys.stdout, '[%s] %s' % (prefix, message)
        return
    prefix_length = len(prefix) + 2
    if prefix_length >= pad:
        padding = ' '
    else:
        padding = ' ' * (pad - prefix_length)
    if len(prefix) > 1:
        prefix = '[%s]' % prefix
    else:
        prefix = '  '
    prefix = '$%s%s$bold%s$reset' % (color.lower(), padding, prefix.upper())
    clean_prefix = ' ' * pad
    data = ' | %s$reset'
    for line in message.split('\n'):
        lines = split_len(line, split_at)
        count = 1
        for current in lines:
            if count == 1:
                text = format_colors(prefix + (data % current))
            else:
                text = format_colors(clean_prefix + (data % current))
            if error:
                print >> sys.stderr, text
            else:
                print >> sys.stdout, text
            count += 1


def error(message, prefix='ERROR', color='red'):
    template(message, prefix, color, True)


def info(message, prefix='INFO', color='cyan'):
    template(message, prefix, color)


def warning(message, prefix='WARNING', color='yellow'):
    template(message, prefix, color)


def success(message, prefix='SUCCESS', color='green'):
    template(message, prefix, color)


def normal(message, prefix, color='white'):
    template(message, prefix, color)
