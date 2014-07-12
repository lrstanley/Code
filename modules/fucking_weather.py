import re
from util.hook import *
from util import web

uri = 'http://www.whatthefuckshouldimakefordinner.com'
re_mark = re.compile(r'<dt><a href="(.*?)" target="_blank">(.*?)</a></dt>')


@hook(cmds=['fuckingweather', 'fw'], ex='fw hell', priority='low')
def fucking_weather(code, input):
    """fw (ZIP|City, State) -- provide a ZIP code or a city state pair to hear about the fucking weather"""
    if not input.group(2):
        return code.say('{red}{b}INVALID FUCKING INPUT. PLEASE ENTER A FUCKING ZIP CODE, OR A FUCKING CITY-STATE PAIR.')
    try:
        text = web.quote(input.group(2))
        data = web.get('http://thefuckingweather.com/?where=%s' % text).read()
        temp = re.compile(
            r'<p class="large"><span class="temperature" tempf=".*?">.*?</p>').findall(data)[0]
        temp = re.sub(r'\<.*?\>', '', temp).strip().replace(' ',
                                                            '').replace('"', '')
        remark = re.compile(r'<p class="remark">.*?</p>').findall(data)[0]
        remark = re.sub(r'\<.*?\>', '', remark).strip()
        flavor = re.compile(r'<p class="flavor">.*?</p>').findall(data)[0]
        flavor = re.sub(r'\<.*?\>', '', flavor).strip()
        return code.say(web.htmlescape(temp) + ' ' + remark + '. ' + flavor)
    except:
        return code.say('{red}{b}I CAN\'T FIND THAT SHIT.')
