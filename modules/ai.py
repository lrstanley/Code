#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
ai.py - Code AI Module
http://code.liamstanley.net/
"""

import random, time

aistate = True
conversation = False
low = 0
high = 1
owner_gone = True
greet_user = ""

greeting = ['Hello', 'Hallo', 'Hi', 'Welcome', 'Ohaider', 'Ello', 'Ohai', 'Hiya']

random.seed()

## Functions that deal with the state of AI being on or off.

def off(code, input):
    if input.nick == code.config.owner:
        code.reply("Feature has been disabled.")
        global aistate
        aistate = False
    else:
        code.reply("You are not authorized to disable this feature.")
off.commands = ['off']
off.priority = 'high'

def on(code, input):
    if input.nick == code.config.owner:
        code.reply("Feature has been enabled.")
        global aistate
        aistate = True
    else:
        code.reply("You are not authorized to enable this feature.")
on.commands = ['on']
on.priority = 'high'

def state(code, input):
    global aistate
    if aistate == True:
        code.reply("It is on.")
    else:
        code.reply("It is off.")
state.commands = ['state']
state.priority = 'high'

## Functions that do not rely on "AISTATE"

#to be set in config
def welcomemessage(code, input):
   try:
       greetchan = code.config.greetchans
       greetchan = str(greetchan)
       excludeuser = code.config.excludeusers
       excludeuser = str(excludeuser)
       global aistate
       if any( [aistate == False, input.nick == code.nick, excludeuser.find("'" + input.sender + "'") > -1, excludeuser.find("'" + input.sender + "'") > -1] )
           return
       elif greetchan.find("'" + input.sender + "'") > -1:
          code.say(random.choice(greeting) + input.nick + ', welcome to ' +  input.sender + '!')
       else: return
   except:
       return
welcomemessage.event = 'JOIN'
welcomemessage.rule = r'.*'
welcomemessage.priority = 'medium'
welcomemessage.thread = False

def goodbye(code, input):
    byemsg = random.choice(('Bye', 'Goodbye', 'Seeya', 'Ttyl'))
    punctuation = random.choice(('!', ' '))
    code.say(byemsg + ' ' + input.nick + punctuation)
goodbye.rule = r'(?i)$nickname\:\s+(bye|goodbye|seeya|cya|ttyl|g2g|gnight|goodnight)'
goodbye.thread = False
goodbye.rate = 30

## Functions that do rely on "AISTATE"

def hau(code, input):
    global aistate
    global conversation
    global greet_user
    greet_user = input.nick
    if aistate == True and greet_user == input.nick:
        time.sleep(random.randint(0,1))
        code.reply("How are you?")
        conversation = True
hau.rule = r'(?i)(hey|hi|hello)\b.*(code|$nickname)\b.*$'

def hau2(code, input):
    hau(code,input)
hau2.rule = r'(?i)(code|$nickname)\b.*(hey|hi|hello)\b.*$'

def gau(code, input):
    global aistate
    global conversation
    global greet_user
    if aistate == True and conversation == True and greet_user == input.nick:
        randmsg = random.choice(["That's good to hear!", "That's great to hear!"])
        time.sleep(random.randint(0,1))
        code.reply(randmsg)
        conversation = False
#gau.rule = '(?i).*(good).*'

def bad(code, input):
    global aistate
    global conversation
    global greet_user
    if input.sender == "#pyohio":
        return
    if aistate == True and conversation == True and greet_user == input.nick:
        randmsg = random.choice(["Sorry to hear about that."])
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
    if (mystr.find(" no ") == -1) and (mystr.find("no ") == -1) and (mystr.find(" no") == -1):
        code.reply("You're welcome.")
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
    # This randomly takes what someone says in the form of "code: <message>" and just spits it back out at the user that said it.
    human = random.random()
    if 0 <= human <= 0.025:
        strinput = input.group()
        nick = code.nick + ":"
        strinput = strinput.split(nick)
        code.reply(strinput[1][1:])
random_resp.rule = r'(?i)$nickname\:\s+(.*)'

def yesno(code,input):
    rand = random.uniform(0,5)
    text = input.group()
    text = text.split(":")
    text = text[1].split()
    time.sleep(rand)
    if text[0] == 'yes':
        code.reply("no")
    elif text[0] == 'no':
        code.reply("yes")
yesno.rule = '(code|$nickname)\:\s+(yes|no)$'
yesno.rate = 15

def ping_reply (code,input):
    text = input.group().split(":")
    text = text[1].split()
    if text[0] == 'PING' or text[0] == 'ping':
        code.reply("PONG")
ping_reply.rule = '(?i)($nickname|code)\:\s+(ping)\s*'
ping_reply.rate = 30

def love (code, input):
    code.reply("I love you too.")
love.rule = '(?i)i.*love.*(code|$nickname).*'
love.rate = 30

def love2 (code, input):
    code.reply("I love you too.")
love2.rule = '(?i)(code|$nickname)\:\si.*love.*'
love2.rate = 30

def love3 (code, input):
    code.reply("I love you too.")
love3.rule = '(?i)(code|$nickname)\,\si.*love.*'
love3.rate = 30

if __name__ == '__main__':
    print __doc__.strip()
