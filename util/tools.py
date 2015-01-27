from lib.dateutil.relativedelta import relativedelta
import hashlib
import time
import re


# Time convert usage
# date(relativedelta(seconds=1207509))
attrs = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
date = lambda delta: [
    '%d %s' % (
        getattr(delta, attr), getattr(delta, attr) > 1 and
        attr or attr[:-1]
    ) for attr in attrs if getattr(delta, attr)]


def relative(**kwargs):
    return date(relativedelta(**kwargs))


def hrt(tmp_time):
    return relative(seconds=int(time.time()) - int(tmp_time))


def hash(string):
    return str(hashlib.md5(string).hexdigest())


def chunks(l, n):
    """ Yield successive n-sized chunks from l. """
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def split_len(seq, length):
    return [seq[i:i + length] for i in range(0, len(seq), length)]


def add_commas(number):
    return "{:,d}".format(number)


def remove_spaces(string):
    """ Remove triple/double and leading/ending spaces """
    while '  ' in string:
        string = string.replace('  ', ' ')
    return string.strip()


def matchflag(string):
    string = string.strip()
    if len(string.split()) > 1:
        return False

    # Default to nickname banning if no wildcards supplied
    if re.match(r'^[^.@!\*]$', string):
        string = "{}!*@*".format(string)

    # Test!test@*
    # test!*@*
    # *!test@*
    # *!test@test.com
    # *!*@test.com
    # *!*@*
    # *@host
    # user!ident@hostname.com
    # us*r!ide*@*name.com

    if re.match(r'^(?:(?:(?:[^.@!/]+\![^.@!/]+)|\*)\@(?:[a-zA-Z0-9\*\-\.\:]+))$', string):
        return True
    else:
        return False


def convertflag(string):
    return string.replace('.', '\\.').replace(r'*', r'.*?').strip()
