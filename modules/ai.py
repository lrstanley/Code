import random
import time
import difflib
from util.hook import *

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

# Functions that deal with the state of AI being on or off.


@hook(cmds=['off'], priority='high')
def off(code, input):
    if input.nick == code.config.owner:
        code.reply('{b}{red}Feature has been disabled.')
        global aistate
        aistate = False
    else:
        code.reply('{b}{red}You are not authorized to disable this feature.')


@hook(cmds=['on'], priority='high')
def on(code, input):
    if input.nick == code.config.owner:
        code.reply('{b}{green}Feature has been enabled.')
        global aistate
        aistate = True
    else:
        code.reply('{b}{red}You are not authorized to enable this feature.')


@hook(cmds=['state', 'aistate'], priority='high')
def state(code, input):
    """check the AI state of Code"""
    global aistate
    if aistate:
        code.say('{b}{green}It is on.')
    else:
        code.say('{b}{red}It is off.')

# Functions that do not rely on "AISTATE"


@hook(rule=r'(?i)$nickname\:\s+(bye|goodbye|seeya|cya|ttyl|g2g|gnight|goodnight)', thread=False, rate=30)
def goodbye(code, input):
    """Goodbye!"""
    byemsg = random.choice(('Bye', 'Goodbye', 'Seeya', 'Ttyl'))
    punctuation = random.choice(('!', ' '))
    code.say(byemsg + ' ' + input.nick + punctuation)


def similar(a, b):
    seq = difflib.SequenceMatcher(a=a.lower(), b=b.lower())
    return seq.ratio()


@hook(event='JOIN')
def welcomemessage(code, input):
    """Sends a welcome message on join to users on join, unless in exclude list"""
    global lastuser  # doesn't sent a message if the last user that joined is the same
    if not hasattr(code.config, 'greetchans'):
        return
    try:
        greetchanlist, greetchans = code.config.greetchans, []
        for channel in greetchanlist:
            greetchans.append(channel.lower())
        try:
            excludeuserlist, excludeusers = code.config.excludeusers, []
            for user in excludeuserlist:
                excludeusers.append(user.lower())
        except:
            excludeusers = []
        global aistate
        if any([
            not aistate, input.nick == code.nick,
            input.nick.lower() in excludeusers,
            similar(lastuser, input.nick) > 0.70
        ]):
            return
        elif input.sender.lower() in greetchans:
            code.say('%s %s, welcome to {b}%s{b}!' % (random.choice(greeting), input.nick, input.sender))
            lastuser = input.nick
            return
    except:
        return


@hook(rule=r'(?i)(hey|hi|hello)\b.*(code|$nickname)\b.*$')
def howareyou(code, input):
    """How are you? auto reply module"""
    text = input.group().lower()
    untext = text
    text = text.split()
    if len(text) > 2 and not untext.find(code.nick.lower()) > -1:
        return
    global aistate
    global conversation
    global greet_user
    greet_user = input.nick
    if aistate and greet_user == input.nick:
        time.sleep(random.randint(0, 2))
        code.reply('How are you?')
        conversation = True


@hook(rule=r'(?i)(code|$nickname)\b.*(hey|hi|hello)\b.*$')
def howareyou2(code, input):
    howareyou(code, input)


@hook(rule=r'(?i).*(good).*$')
def gau(code, input):
    global aistate
    global conversation
    global greet_user
    if aistate and conversation and greet_user == input.nick:
        randmsg = random.choice(['That\'s good to hear!', 'That\'s great to hear!'])
        time.sleep(random.randint(0, 2))
        code.reply(randmsg)
        conversation = False


@hook(rule=r'(?i).*(bad|horrible|awful|terrible).*$')
def bad(code, input):
    global aistate
    global conversation
    global greet_user
    if aistate and conversation and greet_user == input.nick:
        time.sleep(random.randint(0, 2))
        code.reply('Sorry to hear about that.')
        conversation = False


@hook(rule=r'(?i).*(thank).*(you).*(code|$nickname).*$', rate=30)
def ty(code, input):
    human = random.uniform(0, 4)
    time.sleep(human)
    mystr = input.group()
    mystr = str(mystr)
    if (mystr.find(' no ') == -1) and (mystr.find('no ') == -1) and \
       mystr.find(' no') == -1:
        code.reply('You\'re welcome.')


@hook(rule=r'(?i)$nickname\:\s+(thank).*(you).*', rate=30)
def ty2(code, input):
    ty(code, input)


@hook(rule=r'(?i).*(thanks).*(code|$nickname).*', rate=30)
def ty3(code, input):
    ty(code, input)


@hook(rule=r'(?i)$nickname\:\s+(.*)')
def random_resp(code, input):
    human = random.random()
    if 0 <= human <= 0.025:
        strinput = input.group()
        nick = code.nick + ':'
        strinput = strinput.split(nick)
        code.reply(strinput[1][1:])


@hook(rule=r'(code|$nickname)\:\s+(yes|no)$', rate=15)
def yesno(code, input):
    rand = random.uniform(0, 5)
    text = input.group()
    text = text.split(':')
    text = text[1].split()
    time.sleep(rand)
    if text[0] == 'yes':
        code.reply('no')
    elif text[0] == 'no':
        code.reply('yes')


@hook(cmds=['ping', 'lag', 'pong'], rate=30)
def ping_reply(code, input):
    code.reply('PONG')


@hook(rule=r'(?i)i.*love.*(code|$nickname).*', rate=30)
def love(code, input):
    code.reply('I love you too.')


@hook(rule=r'(?i)(code|$nickname)\:\si.*love.*', rate=30)
def love2(code, input):
    return love(code, input)


@hook(rule=r'(?i)(code|$nickname)\,\si.*love.*', rate=30)
def love3(code, input):
    return love(code, input)


@hook(rule=r'(?i)(hi|hello|hey|sup|ello|erro|ohai) $nickname[ \t]*$')
def hello(code, input):
    greeting = random.choice(('Hi', 'Hey', 'Hello', 'sup', 'Ohai', 'Erro', 'Ello', 'Ohaider'))
    punctuation = random.choice(('', '!'))
    code.say('%s %s%s!' % (greeting, input.nick, punctuation))


@hook(rule=r'$nickname!', priority='high', thread=False)
def interjection(code, input):
    code.say(input.nick + '!')
