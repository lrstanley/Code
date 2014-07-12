from util.hook import *
from util import web
import re

uri = 'http://domai.nr/api/json/search?q=%s'


@hook(cmds=['domain'], ex='domain google.com', priority='low')
def domain(code, input):
    """domain <domain> -- Use domain.nr's domain API to find used and unused domains."""
    err, domains = '{red}{b}Unable to find information on that domain name.', [
    ]
    url = input.group(2)
    re_m = re.match(re.compile(r'http[s]?://([a-zA-Z0-9_.]{0,40}.*?)/?'), url)
    if re_m:
        url = re_m.group(1)
    try:
        data = web.json(uri % url)
    except:
        return code.say(err)
    if not data['query']:
        return code.say(err)
    for domain in data['results']:
        status = domain['availability']
        if status in ['taken', 'unavailable']:
            color = 'red'
        elif status == 'tld':
            continue
        elif status == 'available':
            color = 'green'
        elif status == 'maybe':
            color = 'grey'
        else:
            print domain
            continue
        r = '{%s}%s{c}' % (color, domain['domain'])
        domains.append(r.replace('.', '{%s}.' % color))
        # Add colors to the above twice because some clients auto parse URLs.
        # and... hopefully by adding colorcodes in the middle we can prevent
        # that
    code.say('Domains: %s' % ' | '.join(domains))
