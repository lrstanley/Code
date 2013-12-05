#!/usr/bin/env python
"""
Code Copyright (C) 2012-2013 Liam Stanley
weather.py - Code Weather Module
http://code.liamstanley.net/
"""

import re
import urllib, urllib2
import json
import HTMLParser

h = HTMLParser.HTMLParser()

api_key = 'a8881902cd797573d33785cbebda6012'
api_uri = 'https://api.forecast.io/forecast/%s/%s,%s'

def location(name):
    name = urllib.quote(name)
    data = json.loads(urllib2.urlopen('http://ws.geonames.org/searchJSON?q=%s&maxRows=1' % name).read())
    try:
        name = data['geonames'][0]['name']
    except IndexError:
        return None, None, None, None
    country = data['geonames'][0]['countryName']
    lat = data['geonames'][0]['lat']
    lng = data['geonames'][0]['lng']
    return name, country, lat, lng

def weather(code,input):
    if not input.group(2):
        return code.reply('Syntax: \'.weather [<city, state>|<country>|<zip>]\'')
    # Here, we check if it's an actual area, if the geo returns the lat/long then it is..
    name, country, lat, lng = location(input.group(2))
    if not name or not country or not lat or not lng:
        return code.reply('Incorrect location. Please try again!')
    try:
        data = json.loads(urllib2.urlopen(api_uri % (api_key,lat,lng)).read())['currently']
    except:
        return code.reply('Incorrect location. Please try again!')
    output = []
    output.append(code.bold('%s, %s' % (code.color('blue',name), country)))
    # "currently":{"time":1384216660,"summary":"Partly Cloudy","icon":"partly-cloudy-night",
    #"precipIntensity":0,"precipProbability":0,"precipType":"snow","temperature":28.49,
    #"apparentTemperature":20.45,"dewPoint":22.12,"humidity":0.77,"windSpeed":8.19,"windBearing":326,
    #"visibility":8.58,"cloudCover":0.5,"pressure":1017.56,"ozone":314.62}
    if 'summary' in data:
        output.append(data['summary'])
    if 'temperature' in data:
        if data['temperature'] == data['apparentTemperature']:
            # Feels like is the same, don't use both of them
            output.append('%s degrees fahrenheit' % (code.color('blue',data['temperature'] + u'\u2109')))
        else:
            output.append('%s (%s) degrees fahrenheit' % (code.color('blue',data['temperature'] + u'\u2109'),
                                                   code.color('blue',data['apparentTemperature'] + u'\u2109')))
    if 'precipIntensity' in data and 'precipType' in data and 'precipIntensity' in data:
        # Nothing happening
        if data['precipIntensity'] == 0 and 'precipProbability' in data:
            # If probability above 0%
            if data['precipProbability'] != '0':
                output.append('%s\% chance of %s' % (code.color('blue',data['precipProbability']),
                                                    code.color('blue',data['precipType'])))
        # Pricipitation
        else:
            output.append('%s of %s' % (code.color('blue',data['precipType']),
                                        code.color('blue',data['precipIntensity'])))
    if 'dewPoint' in data:
        output.append('Dew: %s' % code.color('blue',data['dewPoint']))
    if 'humidity' in data:
        output.append('Humidity: %s' % code.color('blue',data['humidity']))
    if 'windSpeed' in data:
        output.append('Wind speed: %s (Bearing %s)' % (code.color('blue',data['windSpeed']),
                                                      code.color('blue',data['windBearing'])))
    if 'visibility' in data:
        output.append('Visibility %s' % code.color('blue',data['visibility']))
    if 'cloudCover' in data:
        output.append('Cloud cover: %s ' % code.color('blue',data['cloudCover']))
    if 'pressure' in data:
        output.append('Pressure %s' % code.color('blue',data['pressure']))
    if 'ozone' in data:
        output.append('Ozone level: %s' % code.color('blue',data['ozone']))
    code.say(' | '.join(output))
weather.commands = ['weather']

def fw(code, input):
    """.fw (ZIP|City, State) -- provide a ZIP code or a city state pair to hear about the fucking weather"""
    if not input.group(2):
        return code.reply(code.bold('INVALID FUCKING INPUT. PLEASE ENTER A FUCKING ZIP CODE, OR A FUCKING CITY-STATE PAIR.'))
    try:
        text = urllib.quote(input.group(2))
        data = urllib2.urlopen('http://thefuckingweather.com/?where=%s' % text).read()
        temp = re.compile(r'<p class="large"><span class="temperature" tempf=".*?">.*?</p>').findall(data)[0]
        temp = re.sub(r'\<.*?\>', '', temp).strip().replace(' ','').replace('"','')
        remark = re.compile(r'<p class="remark">.*?</p>').findall(data)[0]
        remark = re.sub(r'\<.*?\>', '', remark).strip()
        flavor = re.compile(r'<p class="flavor">.*?</p>').findall(data)[0]
        flavor = re.sub(r'\<.*?\>', '', flavor).strip()
        return code.reply(h.unescape(temp) +' '+ code.color('red',code.bold(remark)) +'. '+ flavor)
    except:
        return code.reply(code.color('red', code.bold('I CAN\'T FIND THAT SHIT.')))
fw.commands = ['fuckingweather', 'fw']
fw.priority = 'low'

if __name__ == '__main__':
    print __doc__.strip()
