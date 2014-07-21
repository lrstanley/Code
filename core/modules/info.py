from datetime import datetime
from util.hook import *
from subprocess import Popen, PIPE


def git_info():
    p = Popen(["git", "log", "-n 1"], stdout=PIPE)
    tmp = p.stdout.read().split('\n', 3)
    new = []
    for item in tmp:
        item = item.replace('\n', '')
        while '  ' in item:
            item = item.replace('  ', ' ')
        item = item.strip()
        new.append(item)
    commit, author, date, message = new
    commit = commit.split(' ', 1)[1]
    author = author.split(' ', 1)[1]
    date = date.split(' ', 1)[1]
    return commit, author, date, message


@hook(cmds=['version', 'v'], rate=30)
def version(code, input):
    """Try to get version (commit) data from git (if installed)"""
    try:
        commit, author, date, message = git_info()
        code.reply('Running version:')
        code.say(' - {b}Commit{b}: %s ({b}%s{b})' % (commit, message))
        code.say(' - {b}Author{b}: %s' % author)
        code.say(' - {b}Date{b}: %s' % date)
        code.say(' - {b}Source{b}: https://github.com/Liamraystanley/Code/')
    except:
        code.say(
            '%s does not use Github file management. Unable to determine version.' %
            code.nick)


@hook(rule='\x01VERSION\x01', rate=20)
def ctcp_version(code, input):
    commit, author, date = git_info()
    date = date.replace('  ', ' ')

    code.write(
        ('NOTICE', input.nick), '\x01VERSION {0} : {1}\x01'.format(
            commit, date)
    )


@hook(rule='\x01SOURCE\x01', rate=20)
def ctcp_source(code, input):
    code.write(
        ('NOTICE',
         input.nick), '\x01SOURCE https://github.com/Liamraystanley/Code/\x01'
    )
    code.write(
        ('NOTICE', input.nick), '\x01SOURCE\x01'
    )


@hook(rule='\x01PING\s(.*)\x01', rate=10)
def ctcp_ping(code, input):
    text = input.group()
    text = text.replace('PING ', '')
    text = text.replace('\x01', '')
    code.write(
        ('NOTICE', input.nick), '\x01PING {0}\x01'.format(text)
    )


@hook(rule='\x01TIME\x01', rate=20)
def ctcp_time(code, input):
    dt = datetime.now()
    current_time = dt.strftime('%A, %d. %B %Y %I:%M%p')
    code.write(
        ('NOTICE', input.nick), '\x01TIME {0}\x01'.format(current_time)
    )
