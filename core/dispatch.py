import os
import re
import threading
from core.call import call
from core.wrapper import input_wrapper, wrapped


def decode(bytes):
    try:
        text = bytes.decode('utf-8')
    except UnicodeDecodeError:
        try:
            text = bytes.decode('iso-8859-1')
        except UnicodeDecodeError:
            text = bytes.decode('cp1252')
    return text


def dispatch(self, origin, args):
    bytes, event, args = args[0], args[1], args[2:]
    text = decode(bytes)

    for priority in ('high', 'medium', 'low'):
        items = self.commands[priority].items()
        for regexp, funcs in items:
            for func in funcs:
                if event != func.event:
                    continue

                match = regexp.match(text)
                if not match:
                    continue

                code = wrapped(self, origin, text, match)
                input = input_wrapper(code, origin, text, bytes, match, event, args)

                nick = input.nick.lower()
                # blocking ability
                if os.path.isfile("blocks"):
                    g = open("blocks", "r")
                    contents = g.readlines()
                    g.close()

                    try:
                        bad_masks = contents[0].split(',')
                    except:
                        bad_masks = ['']

                    try:
                        bad_nicks = contents[1].split(',')
                    except:
                        bad_nicks = ['']

                    # check for blocked hostmasks
                    if len(bad_masks) > 0:
                        host = origin.host
                        host = host.lower()
                        for hostmask in bad_masks:
                            hostmask = hostmask.replace(
                                "\n", "").strip()
                            if len(hostmask) < 1:
                                continue
                            try:
                                re_temp = re.compile(hostmask)
                                if re_temp.findall(host):
                                    return
                            except:
                                if hostmask in host:
                                    return
                    # check for blocked nicks
                    if len(bad_nicks) > 0:
                        for nick in bad_nicks:
                            nick = nick.replace("\n", "").strip()
                            if len(nick) < 1:
                                continue
                            try:
                                re_temp = re.compile(nick)
                                if re_temp.findall(input.nick):
                                    return
                            except:
                                if nick in input.nick:
                                    return

                if func.thread:
                    targs = (self, func, origin, code, input)
                    t = threading.Thread(target=call, args=targs)
                    t.start()
                else:
                    call(self, func, origin, code, input)
