#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
flip.py - Code Coin Flip Module
http://code.liamstanley.io/
"""

from util.hook import *
import random


@hook(cmds=['coin', 'flip'], ex='flip 3', priority='low')
def flip(code, input):
    """flip [amount] -- Flips # of coins and prints output"""

    if input.group(2):
        if input.group(2).isdigit():
            amount = int(input.group(2))
        else:
            return code.reply('{red}Input must be a number!')
    else:
        amount = 1

    if amount == 1:
        return code.action("flips a coin and gets {b}%s{b}." % random.choice(["heads", "tails"]))
    elif amount == 0:
        return code.action("makes a coin flipping motion with its hands.")
    else:
        heads = int(random.normalvariate(.5 * amount, (.75 * amount) ** .5))
        tails = amount - heads
        return code.action("flips {b}%s{b} coins and gets {b}%s{b} heads and {b}%s{b} tails." % (amount, heads, tails))
