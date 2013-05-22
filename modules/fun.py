#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
fun.py - Fun Module
http://code.liamstanley.net/
"""

import random
#from random import randint

def sexycomment(rand):
    """finds a random comment dependant on what the rating was."""
    rand = int(rand)
    high = ['Now that\'s sexy!', 'Damn!', 'Nice!', 'Sweet!', 'Very sexy!', 'You\'re on fire!']
    medium = ['You could do better..', 'Nice man..', 'That\'s alright..', 'Not as sexy as me!']
    low = ['Try harder next time...', 'Ouch.', 'Uhh...', 'You don\'t even match me!', 'HA!', 'Oh man! DX']
    if rand > 80:
        response = random.choice(high)
    elif rand < 81 and rand > 50:
        response = random.choice(medium)
    else:
        response = random.choice(low)
    return response

def sexymeter(code, input):
    hotuser = ['amber', 'mel', 'alaska', 'zac', 'zacbatt'] #remember, lowercase
    notuser = ['taq', 'taq|away', 'retro', 'retro|away', 'jonny'] #because lazy
    text = input.group().split()
    """.sexymeter <target> - rates <target> on sexiness"""
    if len(text) > 2: return
    try:
        nick = text[1]
        ishot = nick.lower() in hotuser
        isnot = nick.lower() in notuser
        rand = str(random.randint(1,100))
        if len(nick) > 20: 
            code.say(input.nick + code.color('red', ': The syntax is .sexymeter <name>.'))
            return
        if nick.lower() == code.nick.lower():
            nick = 'myself'
            rand = '100'
        elif text[1].lower() in map(str.lower,code.config.admins):
            rand = str(random.randint(81,100))
        elif nick.lower() == 'myself' or nick.lower() == 'me':
            nick = input.nick
        elif ishot:
            rand = str(random.randint(81,100))
        elif isnot:
            rand = str(random.randint(0,20))
        else:
            nick = text[1]
        code.say('Rating %s on a scale of 1-100 of sexiness. Result: %s. %s' % (code.bold(nick), \
            code.bold(rand), code.bold(sexycomment(rand))))
    except:
        nick = input.nick
        ishot = nick.lower() in hotuser
        isnot = nick.lower() in notuser
        if ishot or input.admin:
            rand = str(random.randint(81,100))
        elif isnot:
            rand = str(random.randint(0,20))
        else:
            rand = str(random.randint(1,100))
        code.say('Rating %s on a scale of 1-100 of sexiness. Result: %s. %s' % (code.bold(nick), \
            code.bold(rand), code.bold(sexycomment(rand))))
sexymeter.commands = ['sm', 'sexymeter']
sexymeter.priority = 'medium'
sexymeter.example = '.sexymeter Code'
sexymeter.rate = 30

def slap(code, input):
    """.slap <target> - Slaps <target>"""
    text = input.group().split()
    if len(text) < 2 or text[1].startswith('#'): return
    if text[1].lower() == code.nick.lower() or text[1].lower() == 'everyone' or text[1].lower() == 'himself':
        if (input.nick not in code.config.admins):
            text[1] = input.nick
        else: text[1] = 'himself'
    if text[1].lower() in map(str.lower,code.config.admins):
        if (input.nick not in code.config.admins):
            text[1] = input.nick

    verb = random.choice(('slaps', 'kicks', 'destroys', 'annihilates', 'punches', \
    'roundhouse kicks', 'rusty hooks', 'pwns', 'owns', 'karate chops', 'kills', \
    'disintegrates', 'demolishes', 'Pulverizes'))
    afterfact = random.choice(('to death', 'out of the channel', \
    'into a hole, till death', 'into mid-air disintegration', \
    'into a pancake'))
    code.write(['PRIVMSG', input.sender, ' :\x01ACTION', verb, text[1], afterfact, '\x01'])
slap.commands = ['slap', 'slaps']
slap.priority = 'medium'
slap.rate = 30
if __name__ == '__main__':
    print __doc__.strip()

