import re
from util.hook import *


@hook(cmds=['lmgtfy'], ex='lmgtfy linux', args=True)
def lmgtfy(code, input):
    """Let my Google That For You"""
    lmgtfy = input.group(2)
    lmgtfy = re.sub(r"[^\w\s]", ' ', lmgtfy).replace(".", " ").replace(" ", "+")
    while lmgtfy.find('++') > -1:
        lmgtfy = lmgtfy.replace("++", "+").strip("+")
    while lmgtfy.find(' ') > -1:
        lmgtfy = lmgtfy.replace(" ", "").strip(" ")
    code.reply("http://lmgtfy.com/?q=%s" % lmgtfy)
