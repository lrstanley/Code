#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
soundcloud.py - Code Soundcloud Module
http://code.liamstanley.io/
"""
import json
import urllib2
import thread
import time

# HOST of your shoutcast server
shout_host = 'localhost'

# PORT of your shoutcast server. 8000 (no-quotes) is default.
shout_port = 8000

# The shouldn't ever change.
stats_endpoint = 'statistics?json=1'

l = '\x0312\x02'
r = '\x0f\x02'

ran = False

def shoutcast(code, input):
    """Catch current playing songs from a custom Shoutcast server"""

    # We want to get data, atm...
    data = shout_data()['streams'][0]
    if not data:
        return code.say(code.color('red','Failed to connect!'))

    if data == 1:
        return code.say(code.color('red','There isn\'t a host or port in shoutcast.py!'))
    if data['streamstatus'] == 0:
        return code.say(code.color('red','No songs currently playing!'))

    # With erroring out of the way, continue

    output = []
    try:
        artist, songname = data['songtitle'].split('-',1)
        output.append(songname)
        output.append(artist)
    except:
        output.append(data['songtitle'])
    output.append(data['servertitle'])
    output.append('%skbps' % data['bitrate'])
    global last
    last = output
    return code.say(l + '\x0f\x02 - \x0312'.join(output) + r)
shoutcast.cmds = ['playing', 'shoutcast']
shoutcast.priority = 'medium'
shoutcast.rate = 30


last = ''
def shout_daemon(code, input):
    global ran
    if ran == False:
        return
    print "shout_daemon()"
    while True:
        time.sleep(10)
        print '[DAEMON] Initializing check function again...'
        data = shout_data()['streams'][0]
        if not data:
            return
        if data['streamstatus'] == 0:
            return
        output = []
        try:
            artist, songname = data['songtitle'].split('-',1)
            output.append(songname)
            output.append(artist)
        except:
            output.append(data['songtitle'])
        output.append(data['servertitle'])
        output.append('%skbps' % data['bitrate'])
        global last
        if output == last: # It's the same song, ignore...
           return
        else:
           last = output
        return code.write(['PRIVMSG', '#music'], 'Shoutcast: %s%s%s ' % (l, '\x0f\x02 - \x0302'.join(output), r))

def shoutcast_stats(code, input):
    """Get some statistical data from a custom Shoutcast server"""
    print 'herpderptrains' # DO nothing as of yet..
shoutcast_stats.cmds = ['pstats','playerstats','playingstats']
shoutcast_stats.rate = 30


def shout_data():
    "Pull JSON data from the Shoutcast server"
    if not shout_host or not shout_port:
        return 1
    try:
        r = json.loads(urllib2.urlopen('http://%s:%s/%s' % (str(shout_host), str(shout_port), stats_endpoint), timeout=1).read())
    except:
        return False
    return r

def start_daemon(code, input):
    global ran
    if ran == False:
        ran = True
        print "start_daemon()"
        thread.start_new_thread(shout_daemon, (code, input,))
start_daemon.rule = r'.*'

if __name__ == '__main__':
    print __doc__.strip()
