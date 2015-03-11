from util.hook import *
from util import web
from util import output
from util import database
import re
import socket

base = 'https://www.projecthoneypot.org/ip_%s'
db = []


@hook(rule=r'.*', event='JOIN', rate=10)
def auto_honeypot(code, input):
    """Check joining users against the Project Honeypot Database"""
    if not code.config('honeypot_on_join') or input.nick == code.nick:
        return
    global db

    ip = get_ip(input.host)
    try:
        abuser = check(ip)
    except:
        return output.error('Failed to get IP information. Project Honeypot seems to be down!')
    if abuser:
        # First, we need to check if we've already checked for it, and got a
        # match...
        if ip in db:
            return
        db.append(ip)
        database.set(code.default, db, 'honeypot')
        if code.config('kickban_on_honeypot') and code.chan[input.sender][code.nick]['op']:
            # Wants to kickban, and we've got op. BANHAMMER TIME!
            code.write(['MODE', input.sender, '+b', '*!*@' + input.host])
            code.write(['KICK', input.sender, input.nick], abuser)
        code.say(abuser)


@hook(cmds=['honeypot', 'abuse'], rate=10, args=True)
def honeypot(code, input):
    try:
        ip = get_ip(input.group(2))
        abuser = check(ip)
        if abuser:
            return code.say(abuser)
        else:
            return code.say('{green}This user isn\'t in the honeypot. The IP is likely clean!')
    except:
        return code.say('{red}Failed to check if IP is in the honeypot')


def check(ip):
    ip = str(ip)
    data = web.text(base % web.quote(ip)).replace('\n', '').replace('\r', '')
    items = re.compile(r'<div class="contain">.*?<p>(.*?)</p>').findall(data)
    if not items:
        return
    item = web.striptags(items[0])

    if 'We don\'t have data on this IP currently.' in item:
        return
    elif 'none of its visits have resulted' in item:
        return
    else:
        item = item.split('Below', 1)[0]

    if 'The Project Honey Pot system has ' in item:
        item = item.split('The Project Honey Pot system has ')[1]
        item = item[0].upper() + item[1:]

    if 'This IP has not seen any suspicious activity' in data:
        if 'the IP address' in item:
            item = item.replace('the IP address', '%s' % ip)
        output.warning(str(item) +
                       'This is an old record so it might be invalid.')
        return

    if 'the IP address' in item:
        item = item.replace('the IP address', '{red}%s{c}' % ip)

    if 'Double check your URL to make sure this error' in item:
        return
    return '{b}%s{b}' % item.strip()


def get_ip(hostname):
    if hostname.replace('.', '').isdigit():
        return hostname
    try:
        return socket.gethostbyname(socket.getfqdn())
    except:
        return hostname


def setup(code):
    global db
    db = database.get(code.default, 'honeypot')
    if not db:
        db = []
