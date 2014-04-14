import random
from util.hook import *


@hook(cmds=['rr', 'roulette'], ex='roulette Timothy', rate=20)
def roulette(code, input):
    """Play a little gruesome russian roulette."""
    chance = str(random.randint(1, 6))
    if chance == '1':
        response = '{b}{red}dies! :O'
    else:
        response = '{b}{green}is OK{c}{b}, the chamber was empty!'
    if input.group(2):
        nick = input.group(2)
        if nick.lower() == 'myself' or nick.lower() == code.nick.lower() or \
           nick.lower() == 'me' or nick.lower() == 'himself':
            nick = input.nick
        else:
            nick = input.nick
    else:
        nick = input.nick
    code.say('*Points gun at %s, and pulls the trigger* %s %s' % (nick, nick, response))


@hook(cmds=['slap'], rate=20, args=True)
def slap(code, input):
    """Slaps a person using random methods"""
    text = input.group().split()
    if len(text) < 2 or text[1].startswith('#'):
        return
    if text[1].lower() == code.nick.lower() or text[1].lower() == 'everyone' or \
       text[1].lower() == 'everybody' or text[1].lower() == 'himself':
        if (input.nick not in code.config.admins):
            text[1] = input.nick
        else:
            text[1] = 'himself'
    if text[1].lower() in map(str.lower, code.config.admins):
        if (input.nick not in code.config.admins):
            text[1] = input.nick

    verb = random.choice((
        'slaps', 'kicks', 'destroys', 'annihilates', 'punches',
        'roundhouse kicks', 'rusty hooks', 'pwns', 'owns', 'karate chops',
        'kills', 'disintegrates', 'demolishes', 'Pulverizes'
    ))
    afterfact = random.choice((
        'to death', 'out of the channel', 'into a hole, till death',
        'into mid-air disintegration', 'into a pancake'
    ))
    code.write(['PRIVMSG', input.sender, ' :\x01ACTION', verb, text[1], afterfact, '\x01'])


@hook(cmds=['hug'], rate=5)
def hug(code, input):
    """Hugs <target>"""
    text = input.group().split()
    if len(text) < 2 or text[1].startswith('#'):
        return
    if text[1].lower() == code.nick.lower() or text[1].lower() == 'himself':
        if (input.nick not in code.config.admins):
            text[1] = input.nick
        else:
            text[1] = 'himself'
    types = random.choice(('hugs', 'snuggles'))
    hugtype = random.choice(('real tight', 'strongly', 'like a bear', 'tight', ''))
    code.write(['PRIVMSG', input.sender, ' :\x01ACTION', types, text[1], hugtype, '\x01'])
