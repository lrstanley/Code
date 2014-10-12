import random
from util.hook import *


#def setup(code):
#    code.set('rr', {})



@hook(cmds=['rr', 'roulette'], ex='roulette Timothy', rate=20)
def roulette(code, input):
    """Play a little gruesome russian roulette."""
    gun = [False, False, False, False, False, True]
    restart = False
    if input.group(2):

        nick = input.group(2)
        if nick.lower() == 'myself' or nick.lower() == code.nick.lower() or \
           nick.lower() == 'me' or nick.lower() == 'himself':
            nick = input.nick
        elif nick.lower() == 'reload' or nick.lower() == 'restart':
            nick = input.nick
            restart = True
        else:
            nick = input.nick
    else:
        nick = input.nick

    data = code.get('rr')
    if not data or restart:
        random.shuffle(gun)
        data = gun

    reloaded = '*reloads and ' if len(data) == 6 else '*'

    shot = '%s {b}{red}dies{c}! :O' % nick
    alive = 'The gun clicks.'
    response = shot if data[0] == True else alive
    del data[0]

    code.set('rr', data)

    code.action(reloaded + 'points gun at %s* -- *pulls the trigger* -- %s' % (nick, response))


@hook(cmds=['slap'], rate=5, args=True)
def slap(code, input):
    """Slaps a person using random methods"""
    text = input.group().split()
    if text[1].lower() == code.nick.lower() or text[1].lower() == 'everyone' or \
       text[1].lower() == 'everybody' or text[1].lower() == 'himself':
        if input.admin:
            text[1] = input.nick
        else:
            text[1] = 'himself'
    if text[1].lower() in code.config('admins'):
        if input.admin:
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
    code.action('{} {} {}'.format(verb, text[1], afterfact))


@hook(cmds=['hug'], rate=5, args=True)
def hug(code, input):
    """Hugs <target>"""
    text = input.group().split()
    if text[1].lower() == code.nick.lower() or text[1].lower() == 'himself':
        if not input.nick:
            text[1] = input.nick
        else:
            text[1] = 'himself'
    types = random.choice(('hugs', 'snuggles'))
    hugtype = random.choice(
        ('real tight', 'strongly', 'like a bear', 'tight', ''))
    code.action('{} {} {}'.format(types, text[1], hugtype))
