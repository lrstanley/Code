from util import web
from util.hook import *
from util.tools import add_commas

client = '97c32b1cc8e9875be21f502bde81aaeb'
uri = 'http://api.soundcloud.com/resolve.json?url=http://soundcloud.com/%s/%s&client_id=%s'


@hook(rule=r'.*://(?:www.soundcloud.com|soundcloud.com)/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)(?:/)?.*')
def soundcloud(code, input):
    """Automatically find the information from a soundcloud url and display it
       to users in a channel"""
    try:
        artist = input.group(1)
        title = input.group(2)
        # Should look like 'artist/song'
        data = web.json(uri % (artist, title, client))
        output = []
        # Get date first so we can add to the title
        year, month, day = data['created_at'].split()[0].split('/')
        # Should always have a title
        output.append('{pink}{b}%s{b}{c} ({pink}{b}%s/%s/%s{b}{c})' % (data['title'], month, day, year))
        # Should always have an artist
        output.append('uploaded by {pink}{b}%s{b}{c}' % data['user']['username'])
        # Genre!
        if data['genre']:
            output.append('{pink}{b}' + data['genre'] + '{b}{c}')
        # Playback count, if none, obviously don't add it
        if int(data['playback_count']) > 0:
            output.append('{pink}{b}%s{b}{c} plays' % add_commas(data['playback_count']))
        # Download count, if none, obviously don't add it
        if int(data['download_count']) > 0:
            output.append('{pink}{b}%s{b}{c} downloads' % add_commas(data['download_count']))
        # And the same thing with the favorites count
        if int(data['favoritings_count']) > 0:
            output.append('{pink}{b}%s{b}{c} favs' % add_commas(data['favoritings_count']))
        # Comments too!
        if int(data['comment_count']) > 0:
            output.append('{pink}{b}%s{b}{c} comments' % add_commas(data['comment_count']))
        # Tags!
        if len(data['tag_list'].split()) > 0:
            # Rap "taylor gang" "Hip Hop" "20 joints" traxxfdr
            quote = '"'
            tags = []
            tag_list = data['tag_list'].split()
            multi_word_tag = ''
            for tmp in tag_list:
                if tmp.startswith(quote):
                    # Start of a multi-word tag
                    multi_word_tag = tmp.strip(quote)
                elif tmp.endswith(quote):
                    # End of multi-word tag
                    multi_word_tag += ' ' + tmp.strip(quote)
                    tags.append(multi_word_tag)
                    multi_word_tag = ''
                elif len(multi_word_tag) > 0:
                    # It's a middle-word
                    multi_word_tag += ' ' + tmp
                else:
                    # It's just it's own tag. \o/
                    tags.append(tmp)

            for i in range(len(tags)):
                if len(tags[i].split()) > 1:
                    tags[i] = '(#{pink}{b}"%s"{b}{c})' % tags[i]
                else:
                    tags[i] = '(#{pink}{b}%s{b}{c})' % tags[i]
            output.append(' '.join(tags))
        return code.say(' - '.join(output))
    except:
        return


def convert_time(seconds):  # data[17]
    length = seconds
    lenout = ''
    # if length / 86400: # > 1 day
    #    lenout += '%dd ' % (length / 86400)
    if length / 3600:  # > 1 hour
        lenout += '%dh ' % (length / 3600)
    if length / 60:  # > Minutes
        lenout += '%dm ' % (length / 60 % 60)
        lenout += "%ds" % (length % 60)
    return lenout
