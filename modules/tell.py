import time
from util.hook import *
from util import database
from util import tools


maxchars = 400
db = {}
bot = ''


def setup(code):
    """
        Read the database and globalize the variable on module-load.
        Reading/writing is ONLY done when adding data, removing data,
        or the module is being initialized. Less read-write than the
        old tell.py module.
    """
    global bot
    bot = code.nick
    read_db()


def read_db():
    """Read from the tell database"""
    global db
    db = database.get(bot, 'tell')
    if not db:
        db = {}


def save_db():
    """Save the local db variable to the database"""
    global db
    database.set(bot, db, 'tell')


@hook(cmds=['tell', 'note'], ex='tell Allen PM me your password!', args=True)
def tell(code, input):
    """tell <user> -- Save a note so that when <user> gets on it replays"""
    global db
    if not input.sender.startswith('#'):
        return code.say('{b}You must use this in a channel')

    if len(input.group(2)) < 2:
        return code.say('{red}{b}Invalid usage. Use %shelp tell' % code.prefix)

    location, msg = input.group(2).split(' ', 1)
    if location.lower() in db:
        for entry in db[location.lower()]:
            if msg == entry['msg'] and input.nick.lower() == entry['sender'].lower():
                return code.reply('{red}That message is already pending!')
    curr = int(time.time())
    entry = {'time': curr, 'msg': msg, 'sender': input.nick}
    if not location.lower() in db:
        db[location.lower()] = [entry]
    else:
        db[location.lower()].append(entry)
    save_db()
    code.reply('{b}I\'ll let them know when I see them.')


@hook(rule=r'(.*)', priority='low')
def tell_trigger(code, input):
    """Dispatch notes to users if their name was found in the database"""
    if not input.sender.startswith('#'):
        return

    if input.nick.lower() not in db:
        return

    if not db[input.nick.lower()]:
        return

    count = 0
    lines = 1
    queue = ''
    template = '{b}(%s){b} {b}<%s>{b} %s'
    note_nick = '{blue}{b}%s{b}, you have notes!:{c}' % input.nick
    note_more = '{blue}{b}And more notes..{c}{b}'
    for entry in db[input.nick.lower()]:
        count += 1
        if lines == 1:
            note_msg = note_nick
        else:
            note_msg = note_more
        if (len(queue) + 25 + len(entry['msg'])) > maxchars:
            code.say('%s %s' % (note_msg, queue))
            lines += 1
            queue = template % (time_diff(entry['time']), entry['sender'], entry['msg'])
        else:
            tmp = template % (time_diff(entry['time']), entry['sender'], entry['msg'])
            # if queue:
            #     queue = queue + ' {b}|{b} '
            queue = queue + ' ' + tmp
    if lines == 1:
        note_msg = note_nick
    else:
        note_msg = note_more
    del db[input.nick.lower()]
    save_db()
    code.say('%s %s' % (note_msg, queue))


def time_diff(checked):
    """Get the time, in differences between stored and current"""
    curr = int(time.time())
    return tools.relative(seconds=int(curr - int(checked)))[0] + ' ago'
