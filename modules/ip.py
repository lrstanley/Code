from util.hook import *
from util import web

doc = {
    "invalid": "{red}Invalid input: '.whois [ip|hostname]'{c}",
    "error": "{red}Couldn't receive information for %s{c}",
    "na": "{red}N/A{c}"
}

ignore = ['proxy', 'clone', 'bnc', 'bouncer', 'cloud', 'server']


@hook(cmds=['ip', 'host', 'whois', 'geo', 'geoip'], ex='whois 8.8.8.8')
def ip(code, input):
    """ whois [ip|hostname] - Reverse domain/ip lookup (WHOIS) """
    show = [
        ['hostname', 'Hostname'],
        ['ip', 'IP'],
        ['subdivision', 'Divisions'],
        ['country', 'Country'],
        ['continent', 'Continent'],
        ['accuracy', 'Accuracy'],
        ['latitude', 'Lat'],
        ['longitude', 'Long']
    ]
    if not input.group(2):
        host = input.host.strip()
    else:
        host = input.group(2).strip()
    if '.' not in host or ':' in host or len(host.split()) != 1:
        return code.reply(doc['invalid'])
    host = code.stripcolors(host).encode('ascii', 'ignore')

    # Try to get data from GeoIP server...
    try:
        data = web.json("http://geoip.cf/api/%s" % host, timeout=4)
    except:
        return code.reply(doc['error'] % host)

    # Check if errored or localhost
    if 'country' not in data:
        return code.reply(doc['error'] % host)

    output = []

    # Make list of things to respond with
    for option in show:
        item = data[option[0]]
        if isinstance(item, list):
            item = ', '.join(item)
        else:
            item = str(item)
        if len(item) < 1 or item == host:
            output.append('{blue}%s{c}: %s' % (option[1], doc['na']))
        else:
            output.append('{blue}%s{c}: %s' % (option[1], item))
    return code.say(' {b}|{b} '.join(output))


@hook(rule=r'.*', event='JOIN', rate=10, supress=True)
def geoip(code, input):
    """ GeoIP user on join. """
    if not code.config('geoip_on_join'):
        return

    allowed = [channel.lower() for channel in code.config('geoip_on_join', [])]

    if True in [True if item.lower() in input.host else False for item in ignore] or \
       input.nick == code.nick or not input.channel or input.channel not in allowed:
        return

    try:
        if not re.match(r'^[A-Za-z0-9\.\_\-\:]+$', input.host):
            return
        country = web.text("http://geoip.cf/api/%s/country" % input.host, timeout=4)
        if country:
            code.say('{green}User is connecting from %s' % country)
    except:
        return
