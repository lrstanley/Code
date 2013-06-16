#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
heliohost.py - Code Heliohost Reply Module
About: http://code.liamstanley.net/
"""

import string
import smtplib
from email.mime.text import MIMEText

#defines the help auto-reply state
helpstate = True

#recipient to register for mail lib checking
recipient = "#heliohost"

#prevent email and help spam, check if user was jsut replied to
global lastemail
lastemail = ''
global lasthelp
lasthelp = ''
#to configure auto-response emails upon join, put this in your config, uncommented:
##recipient = ['email1@example.com', 'email2@example.com']
##sender = 'no-reply@example.com'
##mailignores = ['user1', 'user2']
def sendmail(code, input):
    global lastemail
    try:
        recipients = code.config.recipient
        sender = code.config.sender
        ignorelist = str(code.config.mailignores)
        if input.admin or input.nick == code.nick or ignorelist.find("'" + input.nick + "'") > -1 or lastemail.find(input.nick) > -1:
            return
        else:
            s = smtplib.SMTP('localhost')
            s.set_debuglevel(1)
            msg = MIMEText("User " + input.nick + " joined channel: " + input.sender)
            msg['Subject'] = input.nick + " joined " + input.sender
            msg['From'] = sender
            msg['To'] = ", ".join(recipients)
            s.sendmail(sender, recipients, msg.as_string())
            lastemail = input.nick
    except:
        return
sendmail.event = 'JOIN'
sendmail.rule = r'.*'
sendmail.priority = 'medium'
sendmail.thread = False

def signup(code, input): 
    """Signup information"""
    raw = input.group()
    msg = string.lower(raw)
    msg = string.split(msg)
    try:
        if msg[1] == 'stevie':
            try:
                if msg[2] == 'ssl':
                    message = ": To sign up for the %s %s, refer here: http://www.heliohost.org/home/signup/217. Only sign up after midnight PST!" % (code.bold('Stevie'), code.color('purple', '(with SSL)'))
                    if input.sender.startswith('#'):
                        code.say(input.nick + message)
                    else:
                        try:
                            code.write(('PRIVMSG', recipient), msg[3] + message)
                        except:
                            code.say(input.nick + message)
            except:
                message = ": To sign up for %s, refer here: http://www.heliohost.org/home/create-stevie-account. Only sign up after midnight PST!" % code.bold('Stevie')
                if input.sender.startswith('#'):
                    code.say(input.nick + message)
                else:
                    try:
                        code.write(('PRIVMSG', recipient), msg[2] + message)
                    except:
                        code.say(input.nick + message)
        elif any( [msg[1] == 'johnny', msg[1] == 'jonny'] ):
            try:
                if msg[2] == 'ssl':
                    message = ": To sign up for %s %s, refer here: http://www.heliohost.org/home/create-johnny-account."  % (code.bold('Johnny'), code.color('purple', '(with SSL)'))
                    if input.sender.startswith('#'):
                        code.say(input.nick + message)
                    else:
                        try:
                            code.write(('PRIVMSG', recipient), msg[3] + message)
                        except:
                            code.say(input.nick + message)
            except:
                message = ": To sign up for %s, refer here: http://www.heliohost.org/home/signup/218." % code.bold('Johnny')
                if input.sender.startswith('#'):
                    code.say(input.nick + message)
                else:
                    try:
                        code.write(('PRIVMSG', recipient), msg[2] + message)
                    except:
                        code.say(input.nick + message)
        elif any( [raw.find('forum') > -1, raw.find('forums') > -1] ):
            message = ": To sign up on our %s, refer here: http://www.helionet.org/index/index.php?app=core&module=global&section=register" % code.bold('forums')
            if input.sender.startswith('#'):
                code.say(input.nick + message)
            else:
                try:
                    code.write(('PRIVMSG', recipient), msg[2] + message)
                except:
                    code.say(input.nick + message)
    except:
        message = (": You may sign up for " + code.bold('Stevie') + \
                   code.color('blue', ' (which has better uptime)') + ", or " + code.bold('Johnny') + \
                   code.color('blue', ' (has many more features).') + "You may also receive " + \
                   code.bold('SSL') + ", type '" + code.color('purple', '.signup (server) ssl') + \
                   "' for more info.")
        if input.sender.startswith('#'):
            code.say(input.nick + message)
        else:
            try:
                code.write(('PRIVMSG', recipient), msg[1] + message)
            except:
                code.say(input.nick + message)
signup.commands = ['signup', 'register']
signup.example = '.signup stevie ssl'

def uptime(code, input):
    """Post uptime linkage"""
    raw = input.group()
    msg = string.lower(raw)
    msg = string.split(msg)
    message = ": our %s is located at: http://heliohost.grd.net.pl/monitor/" % code.bold('uptime service')
    if input.sender.startswith('#'):
        code.say(input.nick + message)
    else:
        try:
            code.write(('PRIVMSG', recipient), msg[1] + message)
        except:
            code.say(input.nick + message)
uptime.commands = ['uptime', 'up']
uptime.example = '.uptime'

def ircstats(code, input):
    """Post ircstats linkage"""
    raw = input.group()
    msg = string.lower(raw)
    msg = string.split(msg)
    message = ": our %s is located at: http://helio.liamstanley.net" % code.bold('irc stats service')
    if input.sender.startswith('#'):
        code.say(input.nick + message)
    else:
        try:
            code.write(('PRIVMSG', recipient), msg[1] + message)
        except:
            code.say(input.nick + message)
ircstats.commands = ['ircstats', 'is']
ircstats.example = '.ircstats'

def log(code, input):
    """Post log linkage"""
    raw = input.group()
    msg = string.lower(raw)
    msg = string.split(msg)
    message = ': %s is located at: http://heliolog.liamstanley.net' % code.bold('log service')
    if input.sender.startswith('#'):
        code.say(input.nick + message)
    else:
        try:
            code.write(('PRIVMSG', recipient), msg[1] + message)
        except:
            code.say(input.nick + message)
log.commands = ['log', 'logs', 'irclogs']
log.example = '.log'

def helpoff(code, input):
    if input.admin:
        code.reply(code.color('red', 'Auto-reply has been disabled.'))
        global helpstate
        helpstate = False
    else:
        code.reply(code.color('red', 'You are not authorized to disable auto-reply.'))
helpoff.commands = ['helpoff']
helpoff.priority = 'high'

def helpon(code, input):
    if input.admin:
        code.reply(code.color('green', 'Auto-reply has been enabled.'))
        global helpstate
        helpstate = True
    else:
        code.reply(code.color('green', 'You are not authorized to enable auto-reply.'))
helpon.commands = ['helpon']
helpon.priority = 'high'

def help(code, input):
    """Help documentation"""
    global lasthelp
    raw = input.group()
    msg = string.lower(raw)
    msg = string.split(msg)
    if input.admin or helpstate == False or len(raw) >= 20 or lasthelp.find(input.nick) > -1:
        return
    else:
        if raw.find(" help") > -1 or raw.find(".help") > -1 or raw.find("!help") > -1 or \
           raw.find(" support") > -1 or raw.find(".support") > -1 or raw.find("!support") > -1:
            message = ": If an admin is not in the channel to assist you, feel free to post your problem on our forum here: http://www.helionet.org."
            code.say(input.nick + message)
            lasthelp = input.nick
        elif any( [raw.find(" what") > -1 and raw.find(" nameservers") > -1, raw.find("what") > -1 and raw.find("name server") > -1] ):
            message = ": The Heliohost name servers are 'ns1.heliohost.org' and 'ns2.heliohost.org'. More info here: http://www.heliohost.org/home/features/domains."
            code.say(input.nick + message)
            lasthelp = input.nick
        else:
            return
help.rule = r'.*'
help.priority = 'low'
help.thread = False

def cmds(code, input):
    """Help documentation"""
    raw = input.group()
    msg = string.lower(raw)
    msg = string.split(msg)
    message = ": For cmds and information, please type .%s " + \
              "(%s), .%s (%s), or .%s." % (code.color('purple', 'account'), \
              code.color('lightblue', 'renew/suspended/status/delete/move'), code.color('purple', 'signup'), \
              code.color('lightblue', 'stevie/johnny'), code.color('purple', 'help'))
    if input.sender.startswith('#'):
        code.say(input.nick + message)
    else:
        try:
            code.write(('PRIVMSG', recipient), msg[1] + message)
        except:
            code.say(input.nick + message)
cmds.commands = ['cmds', 'cmd']
cmds.example = '.cmds'

def account(code, input):
    """account support linkage"""
    raw = input.group()
    msg = string.lower(raw)
    msg = string.split(msg)
    try:
        if msg[1] == 'scripts':
            message = ": For %s scripts, refer here: http://www.heliohost.org/home/support/scripts." \
                      % code.bold('account management')
            if input.sender.startswith('#'):
                code.say(input.nick + message)
            else:
                try:
                    code.write(('PRIVMSG', recipient), msg[2] + message)
                except:
                    code.say(input.nick + message)
        if any( [msg[1] == 'status', msg[1] == 'queued'] ):
            message = ": To view %s status, refer here: http://www.heliohost.org/home/support/scrip" + \
                      "ts/status." % code.bold('account creation')
            if input.sender.startswith('#'):
                code.say(input.nick + message)
            else:
                try:
                    code.write(('PRIVMSG', recipient), msg[2] + message)
                except:
                    code.say(input.nick + message)
        if any( [msg[1] == 'inactive', msg[1] == 'renew'] ):
            message = ": To renew an %s, refer here: http://www.heliohost.org/home/support/scripts/renew." \
                      % code.bold('inactive account')
            if input.sender.startswith('#'):
                code.say(input.nick + message)
            else:
                try:
                    code.write(('PRIVMSG', recipient), msg[2] + message)
                except:
                    code.say(input.nick + message)
        if any( [msg[1] == 'delete', msg[1] == 'remove'] ):
            message = ": To %s your account, refer here: http://www.heliohost.org/home/support/scripts/delete." \
                      % code.bold('delete')
            if input.sender.startswith('#'):
                code.say(input.nick + message)
            else:
                try:
                    code.write(('PRIVMSG', recipient), msg[2] + message)
                except:
                    code.say(input.nick + message)
        if any( [msg[1] == 'move', msg[1] == 'switch', msg[1] == 'change'] ):
            message = ": To %s your account to %s, refer here: http://wiki.helionet.org/Moving_your_account." \
                      % (code.bold('move'), code.bold('another server'))
            if input.sender.startswith('#'):
                code.say(input.nick + message)
            else:
                try:
                    code.write(('PRIVMSG', recipient), msg[2] + message)
                except:
                    code.say(input.nick + message)
        if any( [msg[1] == 'suspended', msg[1] == 'suspend'] ):
            message = ": if your account has been %s or you have %s, refer here: http://www.helionet.org/index/forum/81-suspended-and-queued-accounts/" \
                      % (code.bold('suspended'), code.bold('queued issues'))
            if input.sender.startswith('#'):
                code.say(input.nick + message)
            else:
                try:
                    code.write(('PRIVMSG', recipient), msg[2] + message)
                except:
                    code.say(input.nick + message)
    except:
        message = ": please type '.%s (%s)' for more information." \
                  % (code.color('purple', 'account'), code.color('lightblue', 'status/renew/delete/move/suspended'))
        if input.sender.startswith('#'):
            code.say(input.nick + message)
        else:
            try:
                code.write(('PRIVMSG', recipient), msg[2] + message)
            except:
                code.say(input.nick + message)
account.commands = ['account', 'act']
account.example = '.account delete'

def forums(code, input):
    """account support linkage"""
    message = ": our forums are located at: http://helionet.org/. Go there for any questions you may have."
    if input.sender.startswith('#'):
        code.say(input.nick + message)
    else:
        try:
            code.write(('PRIVMSG', recipient), msg[1] + message)
        except:
            code.say(input.nick + message)
forums.commands = ['forum', 'forums', 'contact']
forums.example = '.forums'


if __name__ == '__main__': 
   print __doc__.strip()
