def wrapped(self, origin, text, match):
    class CodeWrapper(object):

        def __init__(self, code):
            self.bot = code

        def __getattr__(self, attr):
            sender = origin.sender or text
            if attr == 'reply':
                return lambda msg: self.bot.msg(sender, '{}: {}'.format(origin.nick, msg))
            elif attr == 'say':
                return lambda msg: self.bot.msg(sender, msg)
            elif attr == 'action':
                return lambda msg: self.bot.action(sender, msg)
            return getattr(self.bot, attr)

    return CodeWrapper(self)


def check_perm(origin, trigger):
    """
        Match and figure out if the user that's triggering it matches
        the configured admin/owner/whatever
    """
    for matching in trigger:
        if '!' in matching and '@' in matching:
            # nick!user@host
            trigger_nick, other = matching.split('!', 1)
            trigger_user, trigger_host = other.split('@', 1)
            if trigger_nick.lower() == origin.nick.lower() and \
               trigger_user.lower() == origin.user.lower() and \
               trigger_host.lower() == origin.host.lower():
                return True
            continue
        elif '@' in matching and not matching.startswith('@'):
            # user@host
            trigger_user, trigger_host = matching.split('@', 1)
            if trigger_user.lower() == origin.user.lower() and \
               trigger_host.lower() == origin.host.lower():
                return True
            continue
        elif '@' in matching:
            # @host
            trigger_host = matching[1::]
            if trigger_host.lower() == origin.host.lower():
                return True
            continue
        else:
            # host OR nick
            if matching.lower() == origin.nick.lower() or \
               matching.lower() == origin.host.lower():
                return True
            continue
    return False


def input_wrapper(self, origin, text, bytes, match, event, args):
    class CommandInput(unicode):
        def __new__(cls, text, origin, bytes, match, event, args):
            s = unicode.__new__(cls, text)
            s.sender = origin.sender
            s.nick = origin.nick
            s.user = origin.user
            s.host = origin.host
            s.event = event
            s.bytes = bytes
            s.match = match
            s.group = match.group
            s.groups = match.groups
            s.args = args
            s.trusted = False

            if not hasattr(s, 'data'):
                s.data = {}

            if origin.sender.startswith('#'):
                try:
                    s.op = self.chan[origin.sender][origin.nick]['op']
                    s.voiced = self.chan[origin.sender][origin.nick]['voiced']
                except KeyError:
                    s.op, s.voiced = False, False
            else:
                s.op, s.voiced = False, False

            s.owner = check_perm(origin, [self.config('owner')])
            if s.owner:
                s.admin = True
            else:
                s.admin = check_perm(origin, self.config('admins', []))

            if s.owner or s.admin or s.op:
                s.trusted = True
            return s

    return CommandInput(text, origin, bytes, match, event, args)
