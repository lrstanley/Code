import random
from util.hook import *


@hook(cmds=['sm', 'sexymeter'], ex='sm Code', rate=20)
def sexymeter(code, input):
    """Rate people in terms of sexy, and not!"""
    text = input.group().split()
    if len(text) > 2:
        return
    try:
        name = text[1]
        name = True
    except:
        name = False
    if not name:
        nick = input.nick
        rand = str(random.randint(0, 100))
        code.say(
            'Rating {b}%s{b} on a scale of 1-100 of sexiness. Result: {b}%s{b}. {b}%s{b}' % (nick, rand,
                                                                                             sexycomment(rand)))
    else:
        nick = text[1]
        rand = str(random.randint(0, 100))
        if len(nick) > 20:
            code.say('%s: {red}The syntax is .sexymeter <name>.' % input.nick)
            return
        if nick.lower() == code.nick.lower():
            nick = 'myself'
            rand = '100'
        elif text[1].lower() in code.config('admins', []):
            rand = str(random.randint(81, 100))
        elif nick.lower() == 'myself' or nick.lower() == 'me':
            nick = input.nick
        else:
            nick = text[1]
        code.say(
            'Rating %s on a scale of 1-100 of sexiness. Result: %s. %s' % (nick, rand,
                                                                           sexycomment(rand)))


def sexycomment(rand):
    """finds a random comment dependant on what the rating was."""
    rand = int(rand)
    high = ['Now that\'s sexy!', 'Damn!', 'Nice!',
            'Sweet!', 'Very sexy!', 'You\'re on fire!']
    medium = ['You could do better..', 'Nice man..',
              'That\'s alright..', 'Not as sexy as me!']
    low = ['Try harder next time...', 'Ouch.', 'Uhh...',
           'You don\'t even match me!', 'HA!', 'Oh man! DX']
    if rand == 100:
        response = 'You\'re perfect!'
    if rand > 80:
        response = random.choice(high)
    elif rand == 69:
        response = 'It\'s getting sexy in here!'
    elif rand < 81 and rand > 50:
        response = random.choice(medium)
    elif rand == 0:
        response = 'Wow.. You\'re not even on the scale. :('
    else:
        response = random.choice(low)
    return response
