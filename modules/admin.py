#!/usr/bin/env python
"""
Stan-Derp Copyright (C) 2012-2013 Liam Stanley
Credits: Sean B. Palmer, Michael Yanovich
admin.py - Stan-Derp Admin Module
http://standerp.liamstanley.net/
"""

def join(standerp, input): 
   """Join the specified channel. This is an admin-only command."""
   # Can only be done in privmsg by an admin
   if input.sender.startswith('#'): return
   if input.admin: 
      channel, key = input.group(1), input.group(2)
      if not key: 
         standerp.write(['JOIN'], channel)
      else: standerp.write(['JOIN', channel, key])
join.rule = r'\.join (#\S+)(?: *(\S+))?'
join.priority = 'low'
join.example = '.join #example or .join #example key'

def part(standerp, input): 
   """Part the specified channel. This is an admin-only command."""
   # Can only be done in privmsg by an admin
   if input.sender.startswith('#'): return
   if input.admin: 
      standerp.write(['PART'], input.group(2))
part.commands = ['part', 'leave']
part.priority = 'low'
part.example = '.part #example'

def quit(standerp, input): 
   """Quit from the server. This is an owner-only command."""
   # Can only be done in privmsg by the owner
   if input.sender.startswith('#'): return
   if input.owner: 
      standerp.write(['QUIT'])
      __import__('os')._exit(0)
quit.commands = ['quit']
quit.priority = 'low'

def msg(standerp, input): 
   # Can only be done in privmsg by an admin
   if input.sender.startswith('#'): return
   a, b = input.group(2), input.group(3)
   if (not a) or (not b): return
   if input.admin: 
      standerp.msg(a, b)
msg.rule = (['msg', 'message'], r'(#?\S+) (.+)')
msg.priority = 'low'

def me(standerp, input): 
   # Can only be done in privmsg by an admin
   if input.sender.startswith('#'): return
   if input.admin: 
      msg = '\x01ACTION %s\x01' % input.group(3)
      standerp.msg(input.group(2) or input.sender, msg)
me.rule = (['me', 'action'], r'(#?\S+) (.+)')
me.priority = 'low'

def blocks(standerp, input):
    if not input.admin: return

    STRINGS = {
            "success_del" : "Successfully deleted block: %s",
            "success_add" : "Successfully added block: %s",
            "no_nick" : "No matching nick block found for: %s",
            "no_host" : "No matching hostmask block found for: %s",
            "invalid" : "Invalid format for %s a block. Try: .blocks add (nick|hostmask) standerp",
            "invalid_display" : "Invalid input for displaying blocks.",
            "nonelisted" : "No %s listed in the blocklist.",
            'huh' : "I could not figure out what you wanted to do.",
            }

    if not os.path.isfile("blocks"):
        blocks = open("blocks", "w")
        blocks.write('\n')
        blocks.close()

    blocks = open("blocks", "r")
    contents = blocks.readlines()
    blocks.close()

    try: masks = contents[0].replace("\n", "").split(',')
    except: masks = ['']

    try: nicks = contents[1].replace("\n", "").split(',')
    except: nicks = ['']

    text = input.group().split()

    if len(text) == 3 and text[1] == "list":
        if text[2] == "hostmask":
            if len(masks) > 0 and masks.count("") == 0:
                for each in masks:
                    if len(each) > 0:
                        standerp.say("blocked hostmask: " + each)
            else:
                standerp.reply(STRINGS['nonelisted'] % ('hostmasks'))
        elif text[2] == "nick":
            if len(nicks) > 0 and nicks.count("") == 0:
                for each in nicks:
                    if len(each) > 0:
                        standerp.say("blocked nick: " + each)
            else:
                standerp.reply(STRINGS['nonelisted'] % ('nicks'))
        else:
            standerp.reply(STRINGS['invalid_display'])

    elif len(text) == 4 and text[1] == "add":
        if text[2] == "nick":
            nicks.append(text[3])
        elif text[2] == "hostmask":
            masks.append(text[3].lower())
        else:
            standerp.reply(STRINGS['invalid'] % ("adding"))
            return

        standerp.reply(STRINGS['success_add'] % (text[3]))

    elif len(text) == 4 and text[1] == "del":
        if text[2] == "nick":
            try:
                nicks.remove(text[3])
                standerp.reply(STRINGS['success_del'] % (text[3]))
            except:
                standerp.reply(STRINGS['no_nick'] % (text[3]))
                return
        elif text[2] == "hostmask":
            try:
                masks.remove(text[3].lower())
                standerp.reply(STRINGS['success_del'] % (text[3]))
            except:
                standerp.reply(STRINGS['no_host'] % (text[3]))
                return
        else:
            standerp.reply(STRINGS['invalid'] % ("deleting"))
            return
    else:
        standerp.reply(STRINGS['huh'])

    os.remove("blocks")
    blocks = open("blocks", "w")
    masks_str = ",".join(masks)
    if len(masks_str) > 0 and "," == masks_str[0]:
        masks_str = masks_str[1:]
    blocks.write(masks_str)
    blocks.write("\n")
    nicks_str = ",".join(nicks)
    if len(nicks_str) > 0 and "," == nicks_str[0]:
        nicks_str = nicks_str[1:]
    blocks.write(nicks_str)
    blocks.close()

blocks.commands = ['blocks']
blocks.priority = 'low'
blocks.thread = False

def write_raw(standerp, input):
    if not input.owner: return
    txt = input.bytes[7:]
    standerp.reply(txt)
    txt = txt.encode('utf-8')
    a = txt.split(":")
    standerp.reply(str(a))
    standerp.write([a[0].strip()],a[1].strip(),True)
write_raw.commands = ['write']
write_raw.priority = 'high'
write_raw.thread = False

if __name__ == '__main__': 
   print __doc__.strip()
