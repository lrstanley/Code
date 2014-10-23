import re
import thread
import time
from util import web
from util.hook import *
from util import database
from util import output
from util.tools import hash


auto_check = 5  # Time in seconds to check for new tweets

# Input checking...
r_uid = re.compile(r'\s(@[a-zA-Z0-9_]{1,15})')
r_fullname = re.compile(r'<strong class="fullname">(.*?)</strong>')
r_username = re.compile(
    r'<span class="username">.*?<span>@</span>(.*?)</span>')
r_time = re.compile(r'<td class="timestamp">.*?</td>')
r_tweet = re.compile(r'<tr class="tweet-container">.*?</tr>')
r_url = re.compile(
    r'<a href=".*?" class="twitter_external_link.*?" data-url="(.*?)" dir=".*?" rel=".*?" target=".*?">(.*?)</a>')
r_tweeturl = re.compile(r'href="/(.*?)/status/(.*?)\?p=v')
r_basicurl = re.compile(
    'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

uri_user = 'https://mobile.twitter.com/%s/'
uri_hash = 'https://mobile.twitter.com/search?q=%s&s=typd'


def get_tweets(url, sender_uid=False):
    try:
        data = web.get(url).read().replace('\r', '').replace('\n', ' ')
        data = re.compile(r'<table class="tweet.*?>.*?</table>').findall(data)
    except:
        return
    tweets = []
    for tweet in data:
        try:
            tmp = {}
            tmp['url'] = list(r_tweeturl.findall(tweet)[0])
            tmp['url'] = 'https://twitter.com/%s/status/%s' % (tmp['url'][0], tmp['url'][1])
            tmp['full'] = web.htmlescape(r_fullname.findall(tweet)[0].strip())
            tmp['user'] = r_username.findall(tweet)[0].strip()
            tmp['time'] = web.striptags(r_time.findall(tweet)[0]).strip()
            tweet_data = r_tweet.findall(tweet)[0].strip()
            urls = r_url.findall(tweet_data)
            for url in urls:
                url = list(url)
                tweet_data = tweet_data.replace(url[1], url[0])
            tmp['text'] = web.htmlescape(web.striptags(tweet_data).strip())
            uids = r_uid.findall(' ' + tmp['text'])
            for uid in uids:
                tmp['text'] = tmp['text'].replace(
                    uid, '{purple}{b}@{b}%s{c}' % uid.strip('@')).lstrip()

            # Check if it's a retweet
            if sender_uid:
                if sender_uid.lower().strip('@') != tmp['user'].lower().strip('@'):
                    tmp['text'] = tmp['text'] + \
                        ' ({purple}{b}@{b}%s{c})' % tmp['user']
                    tmp['user'] = sender_uid.strip(
                        '@') + ' {blue}{b}retweeted{c}{b}'
            tweets.append(tmp)
        except:
            continue
    if tweets:
        return tweets
    else:
        return False


def format(tweet):
    return '{teal}(Twitter){c} %s ({purple}{b}@{b}%s{c}) - %s' % (tweet['text'], tweet['user'], tweet['url'])


@hook(cmds=['tw', 'twitter'], ex='twitter liamraystanley', args=True, rate=0)
def twitter(code, input):
    """twitter <hashtag|username> - Return twitter results for search"""
    err = '{red}{b}Unabled to find any tweets with that search!'
    args = input.group(2).strip()
    if args.startswith('#'):
        data = get_tweets(uri_hash % web.quote(args))
        if not data:
            return code.say(err)
        return code.say(format(data[0]))
    else:
        data = get_tweets(uri_user % web.quote(args.strip('@')))
        if not data:
            return code.say(err)
        return code.say(format(data[0]))
    return code.say(err)


def setup(code):
    if not code.config('twitter_autopost'):
        return
    if code.debug:
        output.info('Starting daemon', 'TWITTER')
    thread.start_new_thread(daemon, (code, code.config('twitter_autopost', {}),))


def daemon(code, tc):
    while True:
        time.sleep(auto_check)

        if code.debug:
            output.info('Running check for new tweets', 'TWITTER')
        # Here we do the work...
        for channel in tc:
            for tweet_item in tc[channel]:
                if tweet_item.startswith('#'):  # ID
                    data = get_tweets(uri_hash % web.quote(tweet_item))
                else:
                    data = get_tweets(uri_user %
                                      web.quote(tweet_item), tweet_item)
                if not data:
                    continue
                data = data[0]
                hash_str = hash(data['text'])
                db = database.get(code.default, 'twitter')
                if not db:  # New data on new database, don't output anywhere..
                    database.set(code.default, [hash_str], 'twitter')
                    continue
                if hash_str in db:
                    continue  # Same

                db.append(hash_str)
                database.set(code.default, db, 'twitter')
                msg = format(data)
                code.msg(channel, msg.decode('ascii', 'ignore'))
            db = database.get(code.default, 'twitter')
            if db:
                if len(db) > 200:
                    db = db[-200:]
                    database.set(code.default, db, 'twitter')
