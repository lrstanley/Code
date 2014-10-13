import re


def bind_commands(code):
    code.commands = {'high': {}, 'medium': {}, 'low': {}}

    def bind(code, priority, regexp, func):
        if not hasattr(func, 'name'):
            func.name = func.__name__
        code.commands[priority].setdefault(regexp, []).append(func)

    def sub(pattern, code=code):
        # These replacements have significant order
        pattern = pattern.replace('$nickname', re.escape(code.nick))
        return pattern.replace('$nick', r'%s[,:] +' % re.escape(code.nick))

    for name, func in code.variables.iteritems():
        # print name, func
        code.doc[name] = {'commands': [], 'info': None, 'example': None, 'syntax': None}
        if func.__doc__:
            doc = func.__doc__.replace('\n', '').strip()
            while '  ' in doc:
                doc = doc.replace('  ', ' ')
            if ' -- ' in doc:
                code.doc[name]['syntax'] = code.prefix + doc.split(' -- ', 1)[0]
                code.doc[name]['info'] = doc.split(' -- ', 1)[1]
            else:
                code.doc[name]['info'] = doc
        else:
            doc = None
        if hasattr(func, 'example'):
            example = func.example
            example = code.prefix + example.replace('$nickname', code.nick)
        else:
            example = None
        code.doc[name]['example'] = example
        if not hasattr(func, 'priority'):
            func.priority = 'medium'

        if not hasattr(func, 'thread'):
            func.thread = True

        if not hasattr(func, 'event'):
            func.event = 'PRIVMSG'
        else:
            func.event = func.event.upper()

        if not hasattr(func, 'rate'):
            if hasattr(func, 'commands'):
                func.rate = 3
            else:
                func.rate = 0

        if hasattr(func, 'rule'):
            if isinstance(func.rule, str):
                pattern = sub(func.rule)
                regexp = re.compile(pattern)
                bind(code, func.priority, regexp, func)

            if isinstance(func.rule, tuple):
                # 1) e.g. ('$nick', '(.*)')
                if len(func.rule) == 2 and isinstance(func.rule[0], str):
                    prefix, pattern = func.rule
                    prefix = sub(prefix)
                    regexp = re.compile(prefix + pattern)
                    bind(code, func.priority, regexp, func)

                # 2) e.g. (['p', 'q'], '(.*)')
                elif len(func.rule) == 2 and isinstance(func.rule[0], list):
                    prefix = code.prefix
                    commands, pattern = func.rule
                    for command in commands:
                        command = r'(?i)(\%s)\b(?: +(?:%s))?' % (
                            command, pattern
                        )
                        regexp = re.compile(prefix + command)
                        bind(code, func.priority, regexp, func)

                # 3) e.g. ('$nick', ['p', 'q'], '(.*)')
                elif len(func.rule) == 3:
                    prefix, commands, pattern = func.rule
                    prefix = sub(prefix)
                    for command in commands:
                        command = r'(?i)(\%s) +' % command
                        regexp = re.compile(prefix + command + pattern)
                        bind(code, func.priority, regexp, func)

        if hasattr(func, 'commands'):
            code.doc[name]['commands'] = list(func.commands)
            for command in list(func.commands):
                template = r'(?i)^\%s(%s)(?: +(.*))?$'
                pattern = template % (code.prefix, command)
                regexp = re.compile(pattern)
                bind(code, func.priority, regexp, func)
