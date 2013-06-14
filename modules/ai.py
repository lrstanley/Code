#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
ai.py - Code AI Module
http://code.liamstanley.net/
"""

import random, time
import difflib

aistate = True
conversation = False
low = 0
high = 1
owner_gone = True
greet_user = ''
global lastuser
lastuser = ''
greeting = ['Hello', 'Hi', 'Ello']
random.seed()

## Functions that deal with the state of AI being on or off.

def off(code, input):
    if input.nick == code.config.owner:
        code.reply(code.bold(code.color('red', 'Feature has been disabled.')))
        global aistate
        aistate = False
    else:
        code.reply(code.bold(code.color('red', 'You are not authorized to disable this feature.')))
off.commands = ['off']
off.priority = 'high'

def on(code, input):
    if input.nick == code.config.owner:
        code.reply(code.bold(code.color('green', 'Feature has been enabled.')))
        global aistate
        aistate = True
    else:
        code.reply(code.bold(code.color('red', 'You are not authorized to enable this feature.')))
on.commands = ['on']
on.priority = 'high'

def state(code, input):
    """check the AI state of Code"""
    global aistate
    if aistate == True:
        code.say(code.bold(code.color('green', 'It is on.')))
    else:
        code.say(code.bold(code.color('red', 'It is off.')))
state.commands = ['state', 'aistate']
state.priority = 'high'

## Functions that do not rely on "AISTATE"

def goodbye(code, input):
    """Goodbye!"""
    byemsg = random.choice(('Bye', 'Goodbye', 'Seeya', 'Ttyl'))
    punctuation = random.choice(('!', ' '))
    code.say(byemsg + ' ' + input.nick + punctuation)
goodbye.rule = r'(?i)$nickname\:\s+(bye|goodbye|seeya|cya|ttyl|g2g|gnight|goodnight)'
goodbye.thread = False
goodbye.rate = 30

## Functions that do rely on "AISTATE"

#to be set in config
def similar(a, b):
    seq=difflib.SequenceMatcher(a=a.lower(), b=b.lower())
    return seq.ratio()

def welcomemessage(code, input):
    """sends a welcome message on join to users on join, unless in exclude list"""
    global lastuser #doesn't sent a message if the last user that joined is the same
    try:
        greetchan = code.config.greetchans
        try:
            excludeuser = code.config.excludeusers
            excludeuser = excludeuser.lower()
        except:
            excludeuser = ''
        global aistate
        if any( [aistate == False, input.nick == code.nick, input.nick.lower() in excludeuser, \
                 similar(lastuser, input.nick) > 0.70] ):
            return
        elif input.sender in greetchan:
            code.say('%s %s, welcome to %s!' % (random.choice(greeting), input.nick, \
                    code.bold(input.sender)))
            lastuser = input.nick
        else: return
    except: return
welcomemessage.event = 'JOIN'
welcomemessage.rule = r'.*'
welcomemessage.priority = 'medium'
welcomemessage.thread = False

def howareyou(code, input):
    """How are you? auto reply module"""
    text = input.group().lower()
    untext = text
    text = text.split()
    if len(text) > 2 and not untext.find(code.nick.lower()) > -1: return
    global aistate
    global conversation
    global greet_user
    greet_user = input.nick
    if aistate == True and greet_user == input.nick:
        time.sleep(random.randint(0,1))
        code.reply('How are you?')
        conversation = True
howareyou.rule = r'(?i)(hey|hi|hello)\b.*(code|$nickname)\b.*$'

def howareyou2(code, input):
    howareyou(code,input)
howareyou2.rule = r'(?i)(code|$nickname)\b.*(hey|hi|hello)\b.*$'

def gau(code, input):
    global aistate
    global conversation
    global greet_user
    if aistate == True and conversation == True and greet_user == input.nick:
        randmsg = random.choice(['That\'s good to hear!', 'That\'s great to hear!'])
        time.sleep(random.randint(0,1))
        code.reply(randmsg)
        conversation = False
#gau.rule = '(?i).*(good).*'

def bad(code, input):
    global aistate
    global conversation
    global greet_user
    if input.sender == '#pyohio':
        return
    if aistate == True and conversation == True and greet_user == input.nick:
        randmsg = random.choice(['Sorry to hear about that.'])
        time.sleep(random.randint(0,1))
        code.reply(randmsg)
        conversation = False
bad.rule = '(?i).*(bad|horrible|awful|terrible).*$'

## ADDED Functions that do not rely on "AISTATE"

def ty(code, input):
    human = random.uniform(0,9)
    time.sleep(human)
    mystr = input.group()
    mystr = str(mystr)
    if (mystr.find(' no ') == -1) and (mystr.find('no ') == -1) and \
        (mystr.find(' no') == -1):
        code.reply('You\'re welcome.')
ty.rule = '(?i).*(thank).*(you).*(code|$nickname).*$'
ty.priority = 'high'
ty.rate = 30

def ty2(code, input):
    ty(code,input)
ty2.rule = '(?i)$nickname\:\s+(thank).*(you).*'
ty2.rate = 30

def ty4(code, input):
    ty(code, input)
ty4.rule = '(?i).*(thanks).*(code|$nickname).*'
ty4.rate = 40

def random_resp(code, input):
    # This randomly takes what someone says in the form of "code: <message>" and
    #just spits it back out at the user that said it.
    human = random.random()
    if 0 <= human <= 0.025:
        strinput = input.group()
        nick = code.nick + ':'
        strinput = strinput.split(nick)
        code.reply(strinput[1][1:])
random_resp.rule = r'(?i)$nickname\:\s+(.*)'

def yesno(code,input):
    rand = random.uniform(0,5)
    text = input.group()
    text = text.split(':')
    text = text[1].split()
    time.sleep(rand)
    if text[0] == 'yes':
        code.reply('no')
    elif text[0] == 'no':
        code.reply('yes')
yesno.rule = '(code|$nickname)\:\s+(yes|no)$'
yesno.rate = 15

def ping_reply(code,input):
    text = input.group().lower().split(':')
    text = text[1].split()
    if text[0] == 'ping':
        code.reply('PONG')
ping_reply.rule = '(?i)($nickname|code)\:\s+(ping)\s*'
ping_reply.rate = 30

def ping_reply_cmd(code, input):
    ping_reply(code, input)
ping_reply_cmd.commands = ['ping', 'pong']
ping_reply_cmd.rate = 30

def love(code, input):
    code.reply('I love you too.')
love.rule = '(?i)i.*love.*(code|$nickname).*'
love.rate = 30

def love2(code, input):
    code.reply('I love you too.')
love2.rule = '(?i)(code|$nickname)\:\si.*love.*'
love2.rate = 30

def love3(code, input):
    code.reply('I love you too.')
love3.rule = '(?i)(code|$nickname)\,\si.*love.*'
love3.rate = 30

def hello(code, input): 
   greeting = random.choice(('Hi', 'Hey', 'Hello', 'sup', 'Ohai', 'Erro', 'Ello', 'Ohaider'))
   punctuation = random.choice(('', '!'))
   code.say(greeting + ' ' + input.nick + punctuation)
hello.rule = r'(?i)(hi|hello|hey|sup|ello|erro|ohai) $nickname[ \t]*$'

def interjection(code, input): 
   code.say(input.nick + '!')
interjection.rule = r'$nickname!'
interjection.priority = 'high'
interjection.thread = False


if __name__ == '__main__':
    print __doc__.strip()
