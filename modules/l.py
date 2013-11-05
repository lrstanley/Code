#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
l.py - Module for unique/simple things in the channel #L on irc.esper.net
http://code.liamstanley.net/
"""
import urllib2
import paramiko

def status(code, input):
    if not input.owner: return
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(
        paramiko.AutoAddPolicy())
    ssh.connect('vps.mcnovabuild.tk', username='root', 
        password='standerp')
    stdin, stdout, stderr = ssh.exec_command("/bin/bash /root/check")
    return code.say(stdout.readlines())
status.commands = ['status', 'start']
status.rate = 40

# most of these will clog/slow down the system, but i find that they're needed a lot.

def vps(code, input):
    try:
        a = urllib2.urlopen('http://isup.me/server.liamstanley.net').read()
        b = urllib2.urlopen('http://isup.me/ip.liamstanley.net').read()
        c = urllib2.urlopen('http://isup.me/ip2.liamstanley.net').read()
    except: return code.say(code.color('red', 'failed to query isup.me'))
    if 'is up' in a: a = code.color('green', 'online')
    else: a = code.color('red', 'offline')
    if 'is up' in b: b = code.color('green', 'online')
    else: a = code.color('red', 'offline')
    if 'is up' in c: c = code.color('green', 'online')
    else: a = code.color('red', 'offline')
    code.say('vps-1: %s, vps-2: %s, vps-3: %s' % (a, b, c))
vps.commands = ['vps']
vps.priority = 'low'
vps.rate = 10

def mc(code, input):
    code.say('Minecraft server located at: mc.liamstanley.net')
mc.commands = ['mc', 'minecraft', 'server']
mc.priority = 'low'
mc.rate = 20

def request_bnc(code, input):
    code.say('To request a IRC Bouncer, go to: http://liamstanley.net/bnc.php')
request_bnc.commands = ['bnc', 'requestbnc', 'rbnc']
request_bnc.priority = 'low'
request_bnc.rate = 20

def webchat(code, input):
    code.say('To use the webchat head to: http://chat.liamstanley.net/')
webchat.commands = ['chat']
webchat.priority = 'low'
webchat.rate = 20

def jenkins(code, input):
    code.say('The jenkins server is located at: http://build.liamstanley.net/')
    code.say('Head there for latest bug/release information about me!')
jenkins.commands = ['jenkins', 'build']
jenkins.priority = 'low'
jenkins.rate = 20

def codebot(code, input):
    code.say('Code is an open-source Python IRC bot, head here for more info: http://code.liamstanley.net/')
codebot.commands = ['code', 'ircbot', 'bot']
codebot.priority = 'low'
codebot.rate = 20

def github(code, input):
    code.say('Liam Stanleys public GitHub account is located at: http://github.com/Liamraystanley')
github.commands = ['git', 'github', 'source']
github.priority = 'low'
github.rate = 20

def blog(code, input):
    code.say('Blog site located here: http://blog.liamstanley.net/')
blog.commands = ['blog']
blog.priority = 'low'
blog.rate = 20

def syntax(code, input):
    code.say('Syntax is a open-source PHP IRC bot, head here for more info: http://syntax.liamstanley.net/')
syntax.commands = ['syntax']
syntax.priority = 'low'
syntax.rate = 20

def stanlee(code, input):
    code.say('Stan-Lee is a old fork of the famous Dankirk, head here for more info: http://liamstanley.net/#stanlee')
stanlee.commands = ['stanlee', 'dankirk']
stanlee.priority = 'low'
stanlee.rate = 20

def mcd(code, input):
    code.say('Want to downgrade Minecraft easily? Use this tool: http://liamstanley.net/#mcd')
mcd.commands = ['mcd', 'downgrader', 'downgrade']
mcd.priority = 'low'
mcd.rate = 20
