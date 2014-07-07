import re

def bind_commands(self):
    self.commands = {'high': {}, 'medium': {}, 'low': {}}

    def bind(self, priority, regexp, func):
        if not hasattr(func, 'name'):
            func.name = func.__name__
        self.commands[priority].setdefault(regexp, []).append(func)

    def sub(pattern, self=self):
        # These replacements have significant order
        pattern = pattern.replace('$nickname', re.escape(self.nick))
        return pattern.replace('$nick', r'%s[,:] +' % re.escape(self.nick))

    for name, func in self.variables.iteritems():
        # print name, func
        self.doc[name] = {'commands': [], 'info': None, 'example': None}
        if func.__doc__:
            doc = func.__doc__.replace('\n', '').strip()
            while '  ' in doc:
                doc = doc.replace('  ', ' ')
        else:
            doc = None
        if hasattr(func, 'example'):
            example = func.example
            example = example.replace('$nickname', self.nick)
        else:
            example = None
        self.doc[name]['info'] = doc
        self.doc[name]['example'] = example
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
                func.rate = 5
            else:
                func.rate = 0

        if hasattr(func, 'rule'):
            if isinstance(func.rule, str):
                pattern = sub(func.rule)
                regexp = re.compile(pattern)
                bind(self, func.priority, regexp, func)

            if isinstance(func.rule, tuple):
                # 1) e.g. ('$nick', '(.*)')
                if len(func.rule) == 2 and isinstance(func.rule[0], str):
                    prefix, pattern = func.rule
                    prefix = sub(prefix)
                    regexp = re.compile(prefix + pattern)
                    bind(self, func.priority, regexp, func)

                # 2) e.g. (['p', 'q'], '(.*)')
                elif len(func.rule) == 2 and isinstance(func.rule[0], list):
                    prefix = self.prefix
                    commands, pattern = func.rule
                    for command in commands:
                        command = r'(?i)(\%s)\b(?: +(?:%s))?' % (
                            command, pattern
                        )
                        regexp = re.compile(prefix + command)
                        bind(self, func.priority, regexp, func)

                # 3) e.g. ('$nick', ['p', 'q'], '(.*)')
                elif len(func.rule) == 3:
                    prefix, commands, pattern = func.rule
                    prefix = sub(prefix)
                    for command in commands:
                        command = r'(?i)(\%s) +' % command
                        regexp = re.compile(prefix + command + pattern)
                        bind(self, func.priority, regexp, func)

        if hasattr(func, 'commands'):
            self.doc[name]['commands'] = list(func.commands)
            for command in list(func.commands):
                template = r'(?i)^\%s(%s)(?: +(.*))?$'
                pattern = template % (self.prefix, command)
                regexp = re.compile(pattern)
                bind(self, func.priority, regexp, func)
