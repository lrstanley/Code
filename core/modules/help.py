from util.hook import *


@hook(cmds=['commands', 'cmds'], priority='low')
def commands(code, input):
    """Get a list of function-names (commands), that the bot has."""
    if input.group(2):
        return help(code, input)
    if input.sender.startswith('#'):
        code.reply('I am sending you a private message of all my commands.')
    count = 0
    commands = []
    for module in code.doc:
        if code.doc[module]['commands']:
            commands.append(code.doc[module]['commands'][0])
    commands = list(set(commands))
    count = 0
    tmp, cmds = [], []
    # Make a list, of lists, of lines. :)
    for i in sorted(commands):
        count += 1
        if count == 40:
            # Assume new line!
            cmds.append(tmp)
            tmp, count = [], 0
            tmp.append(code.prefix + i)
        else:
            # Assume appending to tmp
            tmp.append(code.prefix + i)
    cmds.append(tmp)
    code.msg(input.nick, 'Commands I recognize:')
    for line in cmds:
        code.msg(input.nick, '# %s' % (', '.join(line)))
    code.msg(input.nick, ('For help, do \'%shelp example\' where ' +
                          '"example" is the name of the command you want ' +
                          'help for.') % code.prefix)


@hook(cmds=['help'], ex='help fml', rate=30)
def help(code, input):
    if input.group(2):
        mod = None
        for module in code.doc:
            # Assume dictionary...
            if input.group(2).lower() in code.doc[module]['commands'] or \
               input.group(2).lower() == module.lower():
                mod = code.doc[module]
                break
        if not mod:
            return code.reply('{red}{b}There is no such command!')
        # Start responding
        if mod['info']:
            if mod['commands']:
                cmds = mod['commands']
            else:
                cmds = [input.group(2)]
            for i in range(len(cmds)):
                cmds[i] = code.prefix + cmds[i]
            if len(cmds) == 1:
                listcmds = ''
            else:
                listcmds = '{green}(%s){c}' % ', '.join(cmds)
            if mod['syntax']:
                code.say('{b}{purple}Syntax{c} %s{b}: %s' % (listcmds, mod['syntax']))
                code.msg(input.sender, '{b}{purple}Description{c}{b}: %s' % (mod['info']), shorten_urls=False)
            else:
                code.msg(input.sender, '{b}{purple}Help{c} %s{b}: %s' % (listcmds, mod['info']), shorten_urls=False)
        if mod['example']:
            code.say('{b}{purple}Example{c}{b}: %s' % mod['example'])
    else:
        response = (
            'Hi, I\'m a bot. "/msg %s {purple}%scmds{c}" for a list ' +
            'of my commands, or see %s for more general details.')
        code.msg(input.sender, response % (code.nick, code.prefix, code.config('website')), shorten_urls=False)


@hook(cmds=['about'], priority='low', rate=60)
def about(code, input):
    response = (
        code.nick + ' was developed by Liam Stanley and many others. {b}' + code.nick + '{b} is a open-source ' +
        'Python Modular IRC Bot, that serves as a fun, fast, and collective resource ' +
        'for large, and small channels. More info: https://github.com/Liamraystanley/Code'
    )
    code.reply(response)


@hook(cmds=['issue', 'report', 'bug', 'issues'], priority='low', rate=60)
def issue(code, input):
    code.reply('Having an issue with {b}' +
               code.nick + '{b}? Post a bug report here:')
    code.say('https://github.com/Liamraystanley/Code/issues/new')


@hook(rule=r'$nickname!', priority='high', thread=False)
def interjection(code, input):
    code.say(input.nick + '!')
