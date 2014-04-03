#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
magic.py - Code Magic Module
http://code.liamstanley.io/
"""

import random
from util.hook import *

@hook(cmds=['8ball', '8b'], ex='8ball Will I feel better tomorrow?', rate=15)
def magic(code, input):
    """Use the Magic 8 Ball"""
    luck = str(random.randint(1,4))
    # http://en.wikipedia.org/wiki/Magic_8-Ball#Possible_answers
    if luck == '1' or luck == '2':
        # chance: 50% - Affirmative/Green/Bold
        response = random.choice(('It is certain.', 'It is decidedly so.', \
                       'Without a doubt.', 'Yes, definitely.', 'You may rely on it.', \
                       'As I see it yes.', 'Most likely.', 'Outlook good.', 'Yes.', \
                       'Signs point to yes.'))
        response = '{green}' + response
    elif luck == '3':
        # chance: 25% - Negative/Red/Bold
        response = random.choice(('Don\'t count on it.', 'My reply is no.', \
                       'My sources say no.', 'Outlook not so good.', 'Very doubtful.'))
        response = '{red}' + response
    else:
        # chance 25% - Non-Committal/Yellow/Bold
        response = random.choice(('Reply hazy, try again.', 'Ask again later.', \
                       'Better not tell you now.', 'Cannot predict now.', \
                       'Concentrate and ask again.'))
        response = '{yellow}' + response
    code.say('*%s shakes the Magic 8 Ball...* {b}%s{c}{b}' % (code.nick, response))