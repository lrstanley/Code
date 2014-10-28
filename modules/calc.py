import re
import hashlib
from util.hook import *
from util import web

uri = 'http://api.duckduckgo.com/?q=%s&format=json'


@hook(cmds=['c', 'calc', 'calculate'], ex='calc 5 + 3', args=True)
def calc(code, input):
    try:
        data = web.json(uri % web.quote(input.group(2).replace('^', '**')))
        if data['AnswerType'] != 'calc':
            return code.reply('Failed to calculate')
        answer = web.striptags(data['Answer'])
        return code.say(answer)
    except:
        return code.reply('Failed to calculate!')


@hook(cmds=['py', 'python'], ex='py print(int(1.0) + int(3))', args=True)
def py(code, input):
    """python <commands> -- Execute Python inside of a sandbox"""
    query = input.group(2).encode('utf-8')
    uri = 'http://tumbolia.appspot.com/py/'
    try:
        answer = web.get(uri + web.quote(query)).read()
        if answer:
            answer = answer.replace('\n', ' ').replace(
                '\t', ' ').replace('\r', '')
            return code.reply(answer)
        else:
            return code.reply('Sorry, no {b}%s{b}')
    except:
        return code.reply('{red}The server did not return an answer.')


@hook(cmds=['md5', 'hash'], priority='low', args=True)
def md5(code, input):
    """md5 <string> -- Create a md5 hash of the input string"""
    return code.say(hashlib.md5(input.group(2)).hexdigest())


@hook(cmds=['sha256'], priority='low', args=True)
def sha256(code, input):
    """sha256 <string> -- Create a sha256 hash of the input string"""
    return code.say(hashlib.sha256(input.group(2)).hexdigest())


@hook(cmds=['sha512'], priority='low', args=True)
def sha512(code, input):
    """sha512 <string> -- Create a sha512 hash of the input string"""
    return code.say(hashlib.sha512(input.group(2)).hexdigest())
