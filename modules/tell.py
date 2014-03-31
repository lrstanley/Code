#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
tell.py - Code tell Module
http://code.liamstanley.io/
"""

import os, re, time, random
from util.hook import *

maximum = 4

def loadReminders(fn):
    result = {}
    f = open(fn)
    for line in f:
        line = line.strip()
        if line:
            try: tellee, teller, verb, timenow, msg = line.split('\t', 4)
            except ValueError: continue # @@ hmm
            result.setdefault(tellee, []).append((teller, verb, timenow, msg))
    f.close()
    return result

def dumpReminders(fn, data):
    f = open(fn, 'w')
    for tellee in data.iterkeys():
        for remindon in data[tellee]:
            line = '\t'.join((tellee,) + remindon)
            try: f.write(line + '\n')
            except IOError: break
    try: f.close()
    except IOError: pass
    return True

def setup(self):
    fn = self.nick + '-' + self.config.host + '.tell.db'
    self.tell_filename = os.path.join(os.path.expanduser('~/.code'), fn)
    if not os.path.exists(self.tell_filename):
        try: f = open(self.tell_filename, 'w')
        except OSError: pass
        else:
            f.write('')
            f.close()
    self.reminders = loadReminders(self.tell_filename) # @@ tell


@hook(cmds=['tell'], ex='tell George When you get back on, I need your help!', args=True)
def f_remind(code, input):
    teller = input.nick
    # @@ Multiple comma-separated tellees? Cf. Terje, #swhack, 2006-04-15
    if input.group() and (input.group())[1:].startswith("tell"):
        if input.group(2).lower().split()[0] in ['liam', 'lime']: return
        verb = "tell".encode('utf-8')
        line = input.groups()
        line_txt = line[1].split()
        tellee = line_txt[0]
        msg = ' '.join(line_txt[1:])
    else:
        verb, tellee, msg = input.groups()
    #unicode, mate
    verb = verb.encode('utf-8')
    tellee = tellee.encode('utf-8')
    msg = msg.encode('utf-8')

    tellee = tellee.rstrip('.,:;')

    if not os.path.exists(code.tell_filename):
        return

    timenow = time.strftime('%d %b %H:%MZ', time.gmtime())
    whogets = list()
    for tellee in tellee.split(','):
        if len(tellee) > 20:
            code.say("Nickname {b}%s{b} is too long." % (tellee))
            continue
        if not tellee.lower() in (teller.lower(), code.nick): # @@
            warn = False
            if not tellee.lower() in whogets:
                whogets.append(tellee)
                if tellee not in code.reminders:
                    code.reminders[tellee] = [(teller, verb, timenow, msg)]
                else:
                    # if len(code.reminders[tellee]) >= maximum:
                    #   warn = True
                    code.reminders[tellee].append((teller, verb, timenow, msg))
    response = str()
    if teller.lower() == tellee.lower() or tellee.lower() == 'me':
        response = 'You can %s yourself that.' % (verb)
    elif tellee.lower() == code.nick.lower():
        response = "Hey, I'm not that derp you know!"
    else:
        response = "I'll pass that on when %s is around."
        if len(whogets) > 1:
            listing = ", ".join(whogets[:-1]) + " or " + whogets[-1]
            response = response % (listing)
        else:
            response = response % (whogets[0])

    if not whogets: # Only get cute if there are not legits
        rand = random.random()
        if rand > 0.9999: response = "Yeah, yeah"
        elif rand > 0.999: response = "Yeah, sure, whatever"

    code.reply(response)

    dumpReminders(code.tell_filename, code.reminders) # @@ tell


def getReminders(code, channel, key, tellee):
    lines = []
    template = "%s: %s <%s> %s %s %s"
    today = time.strftime('%d %b', time.gmtime())

    for (teller, verb, datetime, msg) in code.reminders[key]:
        if datetime.startswith(today):
            datetime = datetime[len(today) + 1:]
        lines.append(template % (tellee, datetime, teller, verb, tellee, msg))

    try: del code.reminders[key]
    except KeyError: code.msg(channel, 'Er...')
    return lines


@hook(rule=r'(.*)', priority='low')
def message(code, input):
    if not input.sender.startswith('#'): return

    tellee = input.nick
    channel = input.sender

    if not os: return
    if not os.path.exists(code.tell_filename):
        return

    reminders = []
    remkeys = list(reversed(sorted(code.reminders.keys())))
    for remkey in remkeys:
        if not remkey.endswith('*') or remkey.endswith(':'):
            if tellee.lower() == remkey.lower():
                reminders.extend(getReminders(code, channel, remkey, tellee))
        elif tellee.lower().startswith(remkey.rstrip('*:').lower()):
            reminders.extend(getReminders(code, channel, remkey, tellee))

    for line in reminders[:maximum]:
        code.say(line)

    if reminders[maximum:]:
        code.say('{b}Further messages sent privately')
        for line in reminders[maximum:]:
            code.msg(tellee, line)

    if len(code.reminders.keys()) != remkeys:
        dumpReminders(code.tell_filename, code.reminders) # @@ tell

if __name__ == '__main__':
    print __doc__.strip()