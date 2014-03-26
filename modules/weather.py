#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
weather.py - Code Weather Module
http://code.liamstanley.io/
"""

import re
import urllib, urllib2
import json
import HTMLParser
from util.hook import *

user = 'code'
h = HTMLParser.HTMLParser()

api_key = 'a8881902cd797573d33785cbebda6012'
api_uri = 'https://api.forecast.io/forecast/%s/%s,%s'

def location(name):
    name = urllib.quote(name)
    data = json.loads(urllib2.urlopen('http://ws.geonames.org/searchJSON?q=%s&maxRows=1&username=%s' % (name, user)).read())
    try:
        name = data['geonames'][0]['name']
    except IndexError:
        return None, None, None, None
    country = data['geonames'][0]['countryName']
    lat = data['geonames'][0]['lat']
    lng = data['geonames'][0]['lng']
    return name, country, lat, lng

def weather(code,input):
    """weather <city, state|country|zip> - Return weather results for specified address"""
    if empty(code, input): return
    # Here, we check if it's an actual area, if the geo returns the lat/long then it is..
    name, country, lat, lng = location(input.group(2))
    if not name or not country or not lat or not lng:
        return code.reply('{red}{b}Incorrect location. Please try again!')
    try:
        data = json.loads(urllib2.urlopen(api_uri % (api_key,lat,lng)).read())['currently']
    except:
        return code.reply('{red}{b}Incorrect location. Please try again!')
    output = []
    output.append('{b}{blue}%s{b}{c} - {b}{blue}%s{b}{c}' % (name, country))
    degree = u'\u00B0'
    if 'summary' in data:
        output.append('{b}{blue}' + data['summary'] + '{b}{c}')
    if 'temperature' in data:
        if data['temperature'] == data['apparentTemperature']:
            # Feels like is the same, don't use both of them
            output.append('{b}{blue}%s%s{b}{c}' % (data['temperature'],degree))
        else:
            output.append('{b}{blue}%s%s{b}{c} ({b}{blue}%s%s{b}{c})' % (data['temperature'], degree,
                                           data['apparentTemperature'], degree))
    if 'precipIntensity' in data and 'precipType' in data and 'precipIntensity' in data:
        # Nothing happening
        if data['precipIntensity'] == 0 and 'precipProbability' in data:
            # If probability above 0%
            if data['precipProbability'] != '0':
                output.append('{b}{blue}%s\%{b}{blue} chance of {b}{blue}%s{b}{c}' % (data['precipProbability'],
                                                    data['precipType']))
        # Pricipitation
        else:
            output.append('{b}{blue}%s{b}{c} of {b}{blue}%s{b}{c}' % (data['precipType'],data['precipIntensity']))
    if 'dewPoint' in data:
        output.append('{b}{blue}Dew:{b}{c} %s%s' % (data['dewPoint'],degree))
    if 'humidity' in data:
        output.append('{b}{blue}Humidity:{b}{c} %s' % data['humidity'])
    if 'windSpeed' in data:
        output.append('{b}{blue}Wind speed:{b}{c} %smph ({b}{blue}Bearing %s%s{b}{c})' % (data['windSpeed'],
                                                      data['windBearing'],degree))
    if 'visibility' in data:
        output.append('{b}{blue}Visibility{b}{c} %s' % data['visibility'])
    if 'cloudCover' in data:
        output.append('{b}{blue}Cloud cover:{b}{c} %s' % data['cloudCover'])
    if 'pressure' in data:
        output.append('{b}{blue}Pressure{b}{c} %s' % data['pressure'])
    if 'ozone' in data:
        output.append('{b}{blue}Ozone level:{b}{c} %s' % data['ozone'])
    code.say(' | '.join(output))
weather.commands = ['weather']
weather.example = 'weather Eaton Rapids, Michigan'

def fw(code, input):
    """fw (ZIP|City, State) -- provide a ZIP code or a city state pair to hear about the fucking weather"""
    if not input.group(2):
        return code.reply('{red}{b}INVALID FUCKING INPUT. PLEASE ENTER A FUCKING ZIP CODE, OR A FUCKING CITY-STATE PAIR.')
    try:
        text = urllib.quote(input.group(2))
        data = urllib2.urlopen('http://thefuckingweather.com/?where=%s' % text).read()
        temp = re.compile(r'<p class="large"><span class="temperature" tempf=".*?">.*?</p>').findall(data)[0]
        temp = re.sub(r'\<.*?\>', '', temp).strip().replace(' ','').replace('"','')
        remark = re.compile(r'<p class="remark">.*?</p>').findall(data)[0]
        remark = re.sub(r'\<.*?\>', '', remark).strip()
        flavor = re.compile(r'<p class="flavor">.*?</p>').findall(data)[0]
        flavor = re.sub(r'\<.*?\>', '', flavor).strip()
        return code.reply(h.unescape(temp) +' '+ remark +'. '+ flavor)
    except:
        return code.reply('{red}{b}I CAN\'T FIND THAT SHIT.')
fw.commands = ['fuckingweather', 'fw']
fw.example = 'fw 48827'
fw.priority = 'low'

if __name__ == '__main__':
    print __doc__.strip()
