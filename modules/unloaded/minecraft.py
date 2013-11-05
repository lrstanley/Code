#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
minecraft.py - Code Minecraft Module
http://code.liamstanley.net/
"""
# http://stackoverflow.com/questions/3096953/difference-between-two-time-intervals-in-python
# http://hastebin.com/buxunokumi.vbs
# http://www.begent.org/funfact.htm
# http://www.2funny4u.com/random-joke.html
# http://nadh.in/docs/geek_jokes/
import urllib2
import re
import difflib
import time
from threading import Timer
import json, socket, struct
import xml.etree.ElementTree as ET
# By default, this is an excluded module, so Code doesn't pick up minecraft_query as a module
from mc_query import MinecraftQuery

true, false, none = True, False, None # Ignore these.
#=------------------------------------: Begin Configuration :-------------------------------------=#
# General state of the Auto Reply section of this module
#  Note: this will only disable the reaction to ingame triggers
mcstate = True

#  Note: include _, 2, or what your IRC plugin uses if the name in IRC is in use.
#  For example: 'LMC' and 'LMC2' for CraftIRC (it adds a number to the end).
# e.g: bots = {'1': ['2:3', '2:3'],
#              '1': ['2:3', '2:3']}
# (1) #channel-name (with #, e.g, #MyChannel)) (2) Bot-name, e.g, MyBot (3) Method, e.g, 2
# Methods of how your bot looks in IRC: (1) <Username> msg (2) (Username) msg (3) Username: msg
bots = {
        '#L':           ['LMC:1', 'LMC2:1', 'LMC_:1', 'Liam:3', 'Lime:3'],
        #'#MCNOVABUILD': ['NovaBot:1', 'NovaBot2:1', 'NovaBot_:1', 'Liam:1'],
        '##L':          ['Liam:3', 'i:1'],
        '#Shad4w':      ['SBot:3', 'SBot_:3', 'Liam:1']
       }

# This spot is for the HUGE list of possible responses. Please note, that some responses DO
# require other settings listed below to be enabled.
# Most of these are formatted as:
# ['#channel:something to respond with', '#Another:more stuff']
# NOTE: SOME OF THESE ARE MINECRAFT CLASSIC OR PREMIUM MINECRAFT "ONLY"!
server_name = [
               "#L:Liams Personal Server!",
               "#Shad4w:Shad4w's Official Craft +Parkour",
               "#MCNOVABUILD:The Nova Galaxy!"
              ]
websites = [
            '#L:http://liamstanley.net',
            '#MCNOVABUILD:http://mcnovabuild.tk',
            '#Shad4w:http://shad4wmc.tk'
           ]
# If you have forums that are seperate from the main site post here
forums = [
          '#MCNOVABUILD:http://mcnovabuild.enjin.com'
         ]
# Voting location?
votelinks = [
             '#MCNOVABUILD:http://mcnovabuild.tk/vote'
            ]
# Here are most of the Classic Minecraft responses:
CLASSIC_water_lava = ['#Shad4w:Recruit+'] # Rank+ that is able to place Lava/Water
CLASSIC_define = ['#L', '##L', '#Shad4w'] # "What is grief/spleef/tunneling/spam" response

# Channels that are CLASSIC MINECRAFT, can have a playerlist
# Note, there are many flaws with this, one being, by assumption i need to 
# clear the list every 30 minutes. Users that are talking are added to the online
# list, players that quit/get banned/kicked, will be removed, and players
# that are inactive (or leave with /hide on), will be auto removed every 30 minutes.
# If you're not running fCraft/800craft, or a varient of it, the join/quit/ban/kick
# reason might not fit your server. BEWARE.
# Also note: features like .promoratio reuire this to be enabled.
CLASSIC_players = ['#L', '##L', '#Shad4w']
CLASSIC_player_time = 40 # Time in minutes, to purge old users from the list
CLASSIC_player_number = 200 # If not above, you can specify the amount of messages before purge
CLASSIC_method = ['#L:1', '##L:1', '#Shad4w:1'] # 1 = fCraft/800craft, 2 = MCDzienny | If you have another, talk with me
# For use with .plugins
#  Note, to use these on your server, you need query enabled in server.properties
query_enabled = True
query_host = 'play.mcnovabuild.tk'
query_port = 25565
query_channel = '#MCNOVABUILD'

# This section is for "Mineload" (ONLY if you have Mineload installed) (Only one channel for now)
# it can return many things, like: MOTD, playercount/maxplayercount, server load
#   server OS information, and server ticks
# example URL: http://mc.myserver.net:25500/?password=herpderptrains
# More info: 
# - http://dev.bukkit.org/bukkit-mods/mineload/pages/installation-part-1-the-plugin/
# the values in the above link need to be filled in below:
# the CURRENT version of Mineload doesn't support colors in MOTD, or else it breaks!
ml_host = query_host
ml_port = 25500
ml_password = 'standerp'
ml_channel = '#MCNOVABUILD'

# This section is for HTTPConsole" (Only one channel for now)
# - http://dev.bukkit.org/bukkit-plugins/httpconsole/
# Allows the ability for any admin (below) to send a command to the server via .console <command>
# Remember to whitelist the IP of where your bot is located in the HTTPConsole config.
# DO NOT ALLOW "all" IP'S IN HTTPCONSOLE CONFIG! HIGHLY INSECURE!
console = True # Is Console enabled?
console_channel = '#MCNOVABUILD'
console_host = 'vps.mcnovabuild.tk'
console_port = 25505
console_admins = ['Liam', 'Lime', 'Jake0720'] # Users allowed to execute .console
console_whitelist = [] # Specify the ONLY commands that are allowed
console_blacklist = ['op', 'deop' 'promote', 'demote'] # Allow all commands except for these
console_anyone = ['list'] # Commands usable by anyone on IRC (list ".console list") (BE CAREFUL!)
console_players = False # add .players/.list alias to show players. "list" must be added to console_anyone

#=-------------------------------------: End Configuration :--------------------------------------=#

classic_list = {}
old_list = {}
count = {}
chan = ''
purged = False
def purge_list():
    global old_list
    global classic_list
    global purged
    global chan
    #purged = False
    #if not old_list: old_list = [] # if old_list doesn't exist, populate it
    try: old = old_list[chan]
    except:
        old = []
    try: new = classic_list[chan]
    except:
        purged = False
        return
    diff = list(set(new) - set(old))
    old_list[chan] = diff
    classic_list[chan] = diff
    purged = False

def mc_response(code, input):
    """Auto responding unit for things people say/ask/request ingame"""
    # Are we cleared to go?
    data = get_data(input)
    if not data: return
    channel = input.sender.lower()
    global chan
    chan = channel
    ign, msg = data['ign'], data['msg'].lower()
    if CLASSIC_players:
        global classic_list
        global count
        global purged
        # Thread a purge timer
        if CLASSIC_player_time:
            if not purged:
                purged = True
                t = Timer(float(int(CLASSIC_player_time)*60), purge_list)
                t.start()
        elif CLASSIC_player_number:
            try: count[channel] += 1
            except: count[channel] = 0
            number = CLASSIC_player_number
            if count[channel] == number: # have we hit our re-check?
                count[channel] = 0
        # If they're talking and not in the list, add them!
        try:
            if not channel in classic_list: classic_list[channel] = []
            playerlist = classic_list[channel]
        except: playerlist = []
        if not ign in playerlist:
            playerlist.append(ign)
            classic_list[channel] = list(playerlist)
    if not mcstate: return # allow .players, but allow turning of mc-responses without effection
    length = 40 # This is the length of the message that Code should stop checking for
    if len(msg) >= length:
        return # It's too long, and we'll assume they don't need our assistance.
    #-------------------: Begin Responses :-------------------#
    # Server name/MOTD Response
    if server_name and (check(msg,[' what', ' whats ',' what is ']) and \
                        check(msg,[' your ',' you ',' is ',' the ']) and \
                        check(msg,[' server'])):
            data = dynamic_channel_split(input.sender, server_name)
            if not data: return
            r = 'The server name is called: %s'
            return code.say(ign + ': ' + r % (data))
    # Website Response
    if websites and (check(msg,[' what ',' whats ',' what is ',' have ','where are']) and \
                     check(msg,[' site ',' website'])):
            data = dynamic_channel_split(input.sender, websites)
            if not data: return
            r = 'Our website is located at %s!'
            return code.say(ign + ': ' + r % (data))
    # Forum Response
    if forums and (check(msg,[' what ',' whats ',' what is ',' have ','where are']) and \
                  check(msg,[' forum'])):
            data = dynamic_channel_split(input.sender, forums)
            if not data: return
            r = 'Our forum is located at %s!'
            return code.say(ign + ': ' + r % (data))
    # Voting Link Response
    if votelinks and (check(msg,[' where ',' what ']) and \
                      check(msg,[' to ',' website ',' do ']) and \
                      check(msg,[' vote',' voting'])):
            data = dynamic_channel_split(input.sender, votelinks)
            if not data: return
            r = 'You can vote for us at: %s!'
            return code.say(ign + ': ' + r % (data))
    # Classic water/lava Response
    if CLASSIC_water_lava and (check(msg,[' how ',' what ']) and \
                               check(msg,[' get ',' to ',' do ']) and \
                               check(msg,[' water',' lava'])):
            data = dynamic_channel_split(input.sender, CLASSIC_water_lava)
            if not data: return
            r = 'To get water or lava, ask a user ranked %s to place it for you, or type /water or /lava'
            return code.say(ign + ': ' + r % (code.bold(code.color('blue', data))))
    # Classic "What is grief/spleef/tunneling/spam" response
    if CLASSIC_define and (check(msg,[' how ',' what']) and \
                           check(msg,[' whats ',' is ']) and \
                           check(msg,['grief','greif','spleef','spam','tunnel','tower'])) or \
                           (check(msg,['define'],cmd=True)):
            data = dynamic_channel_split(input.sender, CLASSIC_define, rdata=False)
            if not data: return
            cmd = msg.lower().replace('!','',1).replace('.','',1).strip()
            if cmd.split()[0] == 'define' and len(cmd.split()) == 1:
                code.say('Syntax: \'%s <grief|spleef|spam|tunneling|towering>\'' % code.bold('.define'))
            if 'grief' in cmd or 'greif' in cmd:
                r = '%s - The destruction of blocks that aren\'t yours, modification ' + \
                    'of builds that are not yours, or spamming of blocks.'
                w = 'Grief'
            elif 'spleef' in cmd:
                r = '%s - The dustruction of blocks under a person in attempt to bury them.'
                w = 'Spleef'
            elif 'spam' in cmd:
                r = '%s - Either the random placement of blocks on the ground, or ' + \
                    'the form of writing excess content into chat.'
                w = 'Spam'
            elif 'tunnel' in cmd:
                r = '%s - Tunneling in random directions with no purpose, ' + \
                    'other than to just make tunnels.'
                w = 'Tunneling'
            elif 'tower' in cmd:
                r = '%s - The use of blocks to get to a higher location. ' + \
                    'This is fine as long as it\'s removed afterwards.'
                w = 'Towering'
            else: return
            return code.say(ign + ': ' + (r % code.bold(w)))
    #-----------------: No-Config Responses :-----------------#
    # Minecraft Server Status
    if check(msg,['mcstatus','mcs'],cmd=True):
        return mcstatus(code, input)
    # Server load check
    if check(msg,['load','memory'],cmd=True):
        return mineload_response(code, input)
    # Server system info
    if check(msg,['sinfo'],cmd=True):
        return mineload_sinfo(code, input)
    # Spleef timer
    if check(msg,['timer','spleef','go'],cmd=True):
        code.say(code.color('red', '3'))
        code.say(code.color('yellow', '2'))
        code.say(code.color('lime', '1'))
        return code.say(code.color('green', code.bold('GO!')))
    # User Premium Check
    if check(msg,['haspaid','paid'],cmd=True):
        msg = msg.strip().split()
        try: nickname = msg[1]
        except: return code.say(ign + ': The syntax is .haspaid <username>.')
        return code.say(haspaid_check(code, input, nickname))
    # Version Download Tool
    if check(msg,['jar','mcdl'],cmd=True):
        msg = msg.split()
        try: version = msg[1]
        except: return code.say(ign + ': The syntax is .jar <version>.')
        return code.say(mcdl_check(code, input, version))
    if ':test:' in msg: return code.say(repr(ign) + ":" + repr(msg))
mc_response.rule = r'.*'
mc_response.priority = 'high'
#mc_response.rate = 4

def test(code, input):
    if not input.group(2): return code.say('Enter input please.')
    return code.say(repr(input.group()))
test.commands = ['testing', 'repr']
test.rate = 10

def clean_list():
    global classic_list
    global old_list
    global started
    if not old_list:
        old_list = classic_list
        return True
    # For each user in the current list
    try:
        for channel, user in classic_list.iteritems():
            old = old_list[channel]
            new = classic_list[channel]
            if user in old:
                index = new.index(user)
                del new[index]
        classic_list[channel] = new
        old_list = classic_list
    except: pass
    started = False

def classic_parse(code, input):
    data = dynamic_channel_split(input.sender, CLASSIC_players, rdata=False)
    botdata = parse_bots(input.sender, user=input.nick)
    server = int(dynamic_channel_split(input.sender, CLASSIC_method))
    if not data or not botdata or not server: return
    if server == 1: #fCraft/800craft
        if not input.group().startswith(u'\x01ACTION'): return
        msg = stripcolors(input.group()).replace('ACTION','',1).replace('\x01','').strip()
        if not msg.startswith('* '): return # Default Server symbol
    elif server == 2: # MCDzienny, or of the sort
        msg = stripcolors(input.group()).strip()
        if check(msg, [':','<','>','*']): return
    else: return
    global classic_list
    try:
        playerlist = classic_list[input.sender.lower()]
    except: playerlist = []
    msg = msg.replace('~','').replace('#','').replace('+','').replace('*','').replace('@','').replace('\'','')
    msg = re.sub(r'\[.*?\]','',msg)
    while '  ' in msg:
        msg = msg.replace('  ', ' ')
    if ' joined the game.' in msg or ' connected.' in msg:
        # this means the user is connecting!
        try:
            nick = msg.replace(' joined the game.','').replace(' connected.','').replace(' ','')
            if nick in playerlist: return
            playerlist.append(nick)
            classic_list[input.sender.lower()] = playerlist
        except: return
    if ' left the game.' in msg or ' left the server' in msg or \
       ' Ragequit from the server:' in msg:
        # this means the user is leaving!
        try:
            if ' Ragequit from the server' in msg:
                nick = msg.split('Ragequit from the server')[0].strip()
            elif ' left the server' in msg:
                nick = msg.split('left the server')[0].strip()
            else:
                nick = msg.replace(' left the game.','')
            index = playerlist.index(nick.replace(' ',''))
            del playerlist[index]
            classic_list[input.sender.lower()] = playerlist
        except:
            return
    if ' was banned by ' in msg or ' was BanXd (with auto-demote) by ' in msg or ' was banned.' in msg:
        #b-b-b-ban hammer!
        try:
            if ' was banned.' in msg:
                nick = msg.replace(' was banned.','')
            elif ' was banned by ' in msg:
                nick = msg.split('was banned by')[0].strip()
            else:
                nick = msg.split('was BanXd')[0].strip()
            index = playerlist.index(nick.replace(' ',''))
            del playerlist[index]
            classic_list[input.sender.lower()] = playerlist
        except: return
    if ' was kicked by ' in msg or ' was kicked.' in msg or ' kicked (' in msg:
        #User was kicked!
        try:
            if ' was kicked by ' in msg:
                nick = msg.split('was kick by')[0].strip()
            elif ' was kicked.' in msg:
                nick = msg.replace(' was kicked.','')
            else: nick = msg.split('kicked (')[0].strip()
            index = playerlist.index(nick.replace(' ',''))
            del playerlist[index]
            classic_list[input.sender.lower()] = playerlist
        except: return
classic_parse.rule = r'.*'
classic_parse.priority = 'high'                  

def classic_players(code, input):
    data = dynamic_channel_split(input.sender, CLASSIC_players, rdata=False)
    if not data: return
    try: users = classic_list[input.sender.lower()]
    except: return code.say('Nobody minecrafting right now!')
    if len(classic_list[input.sender.lower()]) == 0: return code.say('Nobody minecrafting right now!')
    #code.say(repr(users))
    if len(users) > 20: return code.say('%s Players online.' % code.bold(str(len(users))))
    code.say('%s Players online: %s' % (code.bold(len(users)), \
                                    ', '.join(sorted(users, key=lambda s: s.lower()))))
classic_players.commands = ['players']

def stripcolors(data):
    # STRIP ALL ZE COLORS!!!!!
    colors = [u"\x0300", u"\x0301", u"\x0302", u"\x0303", u"\x0304", u"\x0305", \
              u"\x0306", u"\x0307", u"\x0308", u"\x0309", u"\x0310", u"\x0311", \
              u"\x0312", u"\x0313", u"\x0314", u"\x0315", u"\x03", u"\x02", u"\x09", \
              u"\x13", u"\x0f", u"\x15"]
    for color in colors:
        data = data.replace(color, '')
    return str(data)

def dynamic_channel_split(channel, data, rdata=True):
    if not data: return False# Value doesn't exist
    for part in data:
        if rdata:
            splitdata = part.split(':', 1)
            if len(data) == 1:
                if not part.startswith('#'):
                    return part
                returndata = False
            if len(splitdata) == 2:
                chan = splitdata[0]
                if chan.lower() == channel.lower():
                    return splitdata[1]
                returndata = False
        else:
            if part.lower() == channel.lower():
                return True
            returndata = False
    return returndata

def parse_bots(channel, user=False):
    global bots
    for key, value in bots.iteritems():
        if str(key.lower()) == channel.lower():
            #it's the channel, but is it the bot?
            if user:
                chandata = value
                break
            else: return value
        chandata = False
    if not chandata: return
    names, methods = [], []
    for index in chandata:
        data = index.split(':')
        names.append(data[0].lower())
        methods.append(data[1])
    try:
        name = names.index(user.lower())
        method = methods[name]
    except: return
    return name, method
   

def get_data(input, strip=True, nobot=False):
    """Find data, strip and clean it, and return it as a dictionary. If false data, return false
       which means that the username wasn't findable, and it is not a correct message"""
    if not input.sender.startswith('#'): return
    channel = input.sender
    # Here, we iterate over the keys in the bots dictionary every time get_data(input) is called.
    # At first i thought.. well, very poor programming. then i thought, hell, maybe if we make it
    # Take long enough to respond they'll think it's a real person typing it! ;)
    for key, value in bots.iteritems():
        if str(key.lower()) == channel.lower():
            #it's the channel, but is it the bot?
            ischan = value
            break
        ischan = False
    if not ischan: return
    if nobot: return value
    names = []
    methods = []
    for index in ischan:
        data = index.split(':')
        names.append(data[0].lower())
        methods.append(data[1])
    try:
        name = names.index(input.nick.lower())
        method = int(methods[name])
    except: return
    raw = input.group().encode('ascii', 'ignore')
    if strip:
        raw = stripcolors(raw)
    # Find IGN and qualified MSG
    if method == 1:
        if not '<' in raw or not '>' in raw or raw.index('<') != 0: return
        nick = re.compile(r'<.*?>').findall(raw)[0].replace('<','',1).replace('>','',1)
        msg = raw.split('> ',1)[1]
    elif method == 2:
        if not '(' in raw or not ')' in raw or raw.index('(') != 0: return
        nick = re.compile(r'\(.*?\)').findall(raw)[0].replace('(','',1).replace(')','',1)
        msg = raw.split(') ',1)[1]
    elif method == 3:
        if not ':' in raw: return
        nick, msg = raw.split(':',1)
    else: return
    # removes nickname change identifiers used in Essentials, and common rank
    # identifiers (Commonly used in Minecraft Classic)
    nick = nick.replace('~','').replace('#','').replace('+','')
    nick = nick.replace('*','').replace('@','') # Some for classic Minecraft
    nick = re.sub(r'\[.*?\]','',nick)
    if len(nick) > 20: return # 18 just incase the user ingame is using a nick of some sort
    msg = msg.strip().strip("'")
    return {'channel': input.sender,
            'bot': input.nick,
            'ign': nick,
            'msg': msg,
            'method': method}
#    except: return

def check(msg, chklst, cmd=False):
    """Test if a list of things are contained in the input (qualified) message"""
    if cmd:
        if len(msg) < 2: return False # Message hella short!
        msg = msg.strip().split()
        for item in chklst:
            if item.lower().strip('!').strip('.') == msg[0].lower().strip('!').strip('.'):
                if msg[0].startswith('!') or msg[0].startswith('.'):
                    return True
        return False
    else:# bit of padding, just in case
        re.sub(r'[^\w]', '', msg)
        if len(msg) < 2: return False # Message hella short!
        msg = " " + msg.strip() + " "
        for item in chklst:
            if item.lower() in msg:
                return True
        return False

def similar(a, b):
    seq=difflib.SequenceMatcher(a=a.lower(), b=b.lower())
    return seq.ratio()

def mc_off(code, input):
    """.mcoff - Disable the in-game auto reply. Note, this does not toggle all Minecraft
       replies, just the ones from ingame."""
    if input.admin:
        code.reply(code.color('red', 'Minecraft replies have been disabled.'))
        global mcstate
        mcstate = False
    else:
        code.reply(code.color('red', 'You are not authorized to disable this.'))
mc_off.commands = ['mcoff']
mc_off.priority = 'medium'

def mc_on(code, input):
    """.mcon - Enable the in-game auto reply. Note, this does not toggle all Minecraft
       replies, just the ones from ingame."""
    if input.admin:
        code.reply(code.color('green', 'Minecraft replies have been enabled.'))
        global mcstate
        mcstate = True
    else:
        code.reply(code.color('green', 'You are not authorized to enable this.'))
mc_on.commands = ['mcon']
mc_on.priority = 'medium'

def mcstatus(code, input):
    """.mcstatus - Checks the status of the Mojang Minecraft servers."""
    try:
        request = urllib2.urlopen('http://status.mojang.com/check')
        request = request.read()
    except:
        return code.say('minecraft.net returned an error, is it up?')
    # format it, manually
    data = json.loads(request.replace("}", "").replace("{", "").replace("]", "}").replace("[", "{"))
    out = []
    # use a loop, so if they add servers, we don't need to worry
    for server, status in data.items():
        if status == 'green':
            out.append('%s is %s' % (code.color('purple', server), code.color('green', code.bold('online'))))
        else:
            out.append('%s is %s' % (code.color('purple', server), code.color('green', code.bold('offline'))))
    return code.say(' '.join(out))
mcstatus.commands = ['mcs', 'mcstatus', 'mcservers']
mcstatus.example = '.mcs'
mcstatus.rate = 20

def mineload():
    """Mineload XML webpage integration"""
    if mineload_enabled:
        try:
            r = urllib2.urlopen('http://%s:%s/?password=%s' % (ml_host, str(ml_port), ml_password)).read()
            if 'Encoding error' in r: return False # Encoding error. REMOVE COLORS FROM MOTD.
            load = ET.fromstring(r)
            a, b = [], []
            for child in load:
                a.append(child.tag), b.append(child.text)
            c = {}
            for d in range(0, len(a)):
                c[a[d]] = b[d]
            return c
        except: return
    else: return

def mineload_response(code, input):
    """Mineload command hook"""
    if ml_channel.lower() != input.sender.lower(): return
    ml = mineload()
    if not ml: return code.say('Failed to connect to server, is it up?')
    # Code: curr/max Players | % RAM | # % TPS
    players = ml['playercount'] + '/' + ml['maxplayers']
    ram = int((float(ml['memoryused']) / float(ml['maxmemory'])) * 100)
    ticks = int((float(ml['heartbeat']) / 1000) * 100)
    code.say('Players: %s | Memory: %s | Heartrate: %s' % (code.bold(players), \
             code.bold(str(ram))+'%', code.bold(str(ticks))+'%'))
mineload_response.commands = ['load', 'memory', 'performance']
mineload_response.example = '.load'
mineload_response.rate = 10

def mineload_sinfo(code, input):
    """Mineload server info command hook"""
    if ml_channel.lower() != input.sender.lower(): return
    ml = mineload()
    if not ml: return code.say('Failed to connect to server, is it up?')
    # Code: Java: V | OS: N (V) | dir: PWD | Bukkit: V
    code.say('Java: %s | OS: %s (%s) | dir: %s | Bukkit: %s' % (code.bold(ml['jvmversion']), \
            code.bold(ml['osname']), code.bold(ml['osversion']), code.bold(ml['cwd']), \
            code.bold(ml['bukkitversion'])))
mineload_sinfo.commands = ['sinfo']
mineload_sinfo.example = '.sinfo'
mineload_sinfo.rate = 10

def haspaid_check(code, input, nickname):
    """headless haspaid function"""
    if len(nickname) < 2 or len(nickname) > 16: return 'Please enter a correct Minecraft Username.'
#    uri = 'https://minecraft.net/haspaid.jsp?user=%s'
#    req = urllib2.Request(uri % nickname)
#    try: response = urllib2.urlopen(req)
    try: r = urllib2.urlopen('https://minecraft.net/haspaid.jsp?user=%s' % nickname).read()
    except: return code.color('red', 'minecraft.net did not respond correctly, is it down?')
#    fresp = response.read()
    if 'true' in r:
        return 'User %s %s purchased Minecraft.' % (code.color('purple', nickname), code.bold('has'))
    else:
        return 'User %s %s purchased Minecraft.' % (code.color('purple', nickname), code.bold('has not'))

def haspaid(code, input):
    """.haspaid <name> - checks to see if a Minecraft username is premium"""
    if not input.group(2): return code.reply('Please enter a Minecraft username.')
    nickname = input.group(2)
    response = haspaid_check(code, input, nickname)
    code.say(response)
haspaid.commands = ['haspaid', 'paid', 'ispaid']
haspaid.example = '.haspaid liamraystanley'
haspaid.rate = 10

def mcdl_check(code, input, version):
    """ headless mcdl function"""
    if len(version) < 3 or len(version) > 5:
        return 'Please enter a correct Minecraft version. (e.g 1.5.1)'
    oversion = version
    version = version.replace('.', '_')
    uri = 'http://assets.minecraft.net/%s/minecraft.jar'
    req = urllib2.Request(uri % version)
    try: response = urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        if e.code == 404:
            return code.color('red', 'Minecraft version \'%s\' doesn\'t exist!' % code.bold(oversion))
        else: return code.color('red', 'minecraft.net did not respond correctly, is it down?')
        return
    fresp = response.read()
    return code.color('red', (uri % version))

def mcdl(code, input):
    """.mcdl <version> - Gives a link to download that version of Minecraft. Checks if link
       actually exists, before giving back to to the user."""
    if not input.group(2): return code.reply('Please enter a correct Minecraft version. (e.g 1.5.1)')
    version = input.group(2)
    response = mcdl_check(code, input, version)
    code.say(response)
mcdl.commands = ['mcdl', 'mcl', 'mcj', 'jar']
mcdl.example = '.jar 1.5.2'
mcdl.rate = 10

def plugins(code, input):
    try:
        plugins = mcquery('plugins')
        if not plugins: return
        for a in range(0, len(plugins)):
            plugins[a] = plugins[a].split()[0]
        code.say(', '.join(sorted(plugins)))
    except: return code.say(code.color('red', 'Could not connect to server!'))
plugins.commands = ['plugins']
plugins.example = '.plugins'
plugins.rate = 30

def mcquery(query):
    """Hook into the Minecraft Query system. Query port must be open on the server!"""
    if query_host and query_enabled and query_channel.lower() == input.sender.lower():
        mcquery = MinecraftQuery(query_host, query_port)
        response = mcquery.get_rules()
        coolstuff = response[query]
        return coolstuff
    else: return
#    basic_status = query.get_status()
#    full_info = query.get_rules()

def mcping_retrieve(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        sock.send('\xfe\x01')
        response = sock.recv(1)

        if response[0] != '\xff':
            return "Server gave invalid response: " + repr(response)
        length = struct.unpack('!h', sock.recv(2))[0]

        values = sock.recv(length * 2).decode('utf-16be')

        data = values.split(u'\x00')  # try new format
        if len(data) == 1:
            # old format
            data = values.split(u'\xa7')
            message = u"{} - {}/{} players".format(data[0], data[1], data[2])
        else:
            message = u"{} \x0f- \x02{}\x02 - \x0303\x02{}/{}\x02\x03 Players".format(data[3], data[2], data[4], data[5])

        sock.close()
        return message

    except:
        return 'Error pinging ' + host + ':' + str(port) + \
        ', is it up? Double-check your address!'

def mcconvert(motd):
    empty = ''
    colors = [u"\x0300,\xa7f", u"\x0301,\xa70", u"\x0302,\xa71", u"\x0303,\xa72", \
              u"\x0304,\xa7c", u"\x0305,\xa74", u"\x0306,\xa75", u"\x0307,\xa76", \
              u"\x0308,\xa7e", u"\x0309,\xa7a", u"\x0310,\xa73", u"\x0311,\xa7b", \
              u"\x0312,\xa71", u"\x0313,\xa7d", u"\x0314,\xa78", u"\x0315,\xa77", \
              u"\x02,\xa7l", u"\x0310,\xa79", u"\x09,\xa7o", u"\x13,\xa7m", \
              u"\x0f,\xa7r", u"\x15,\xa7n"];
    for s in colors:
        lcol = s.split(',')
        motd = motd.replace(lcol[1], lcol[0])
    motd = motd.replace(u"\xa7k", empty)
    return motd

def mcping(code, input):
    """.mcping <server>[:port] - Check the status of a minecraft server"""
    if input.group(2): text = input.group(2).strip()
    elif query_host and query_enabled:
        text = str(query_host) + ':' + str(query_port)
    else: return code.say('The syntax is: ".mcping my.hostname.net[:port]"')
    stext = text.split()
    if ':' in text and len(stext) == 1:
        host, port = text.split(':', 1)
    elif len(stext) == 2:
        host = stext[0]
        port = stext[1]
    elif len(stext) == 1:
        host = text
        port = 25565
    try:
        port = int(port)
    except:
        return code.say('Error: invalid port!')
    response = mcconvert(mcping_retrieve(host, port))
    if 'is it up' in response:
        return code.say('Error pinging %s, is it up? Re-check your address!' % code.bold(text))
    else:
        return code.say(response)
mcping.commands = ['mcping', 'mcp']

def console(code, input):
    if input.sender.lower() != console_channel.lower():
        if input.sender.startswith('#'): return
    command = input.group(2)
    if input.group(1).lower() == 'players' or input.group(1).lower() == 'list':
        if console_players:
            command = 'list'
        else: return
    if not command: return code.say('Syntax: ".console <command>"')
    base = command.split()[0]
    if command.lower() == 'help' or command.lower() == '?':
        return code.say('Syntax: ".console <command>"')
    # Convert the lists to lowercase, to avoid un-wanted usage
    admins = [x.lower() for x in console_admins]
    wl, bl = [x.lower() for x in console_whitelist], [x.lower() for x in console_blacklist]
    anyone = [x.lower() for x in console_anyone]
    if not input.nick.lower() in admins and not base.lower() in anyone:
        return code.reply('You are not in the admin list!')
    if not wl: # No whitelist
        if base.lower() in bl: return code.reply('That command isn\'t allowed!')
    elif wl and not base.lower() in wl: return code.reply('That command isn\'t allowed!')
    r = console_execute(command.replace(' ','%20'))
    if r == None:
        return code.say('Command executed with no response.')
    elif r == False:
        return code.say('Command Failed to execute. Is the server up?')
    else: return code.say(r)
console.commands = ['console', 'players', 'list']
console.priority = 'medium'

def console_execute(command):
    """command = the command to send to an HTTP url, hosted by HTTPConsole via a bukkit server.
       if server returns a response, data is returned to the user"""
    if not console or not console_host or not console_port: return False
    try:
       r = urllib2.urlopen('http://%s:%s/console?command=%s' % (console_host, str(console_port), command)).read()
    except urllib2.HTTPError as e:
       return False
    r =  r.replace('\t',' ').replace('\r',' ').replace('\n',' ').replace('/','')
    r = re.sub(r'\xa7.','',r)
    nonrcmds = ['stop', 'reload', 'restart', 'start']
    if command.lower() in nonrcmds:
        return 'Executed server status command, no output.'
    elif 'Unknown command' in r:
        return '\x0304Unknown command, please try again.\x03'
    while '--' in r:
        r = r.replace('--','-')
    else: return r


if __name__ == '__main__':
    print __doc__.strip()
