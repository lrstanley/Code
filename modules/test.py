from util.hook import *


@hook(rule=r'.*', event='004')
def test(code, input):
    print 'THIS IS A TEST'
