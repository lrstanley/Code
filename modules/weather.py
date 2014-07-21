from util import web
from util.hook import *

user = 'code'

api_key = 'a8881902cd797573d33785cbebda6012'
api_uri = 'https://api.forecast.io/forecast/%s/%s,%s'


def location(name):
    name = web.quote(name)
    data = web.json(
        'http://ws.geonames.org/searchJSON?q=%s&maxRows=1&username=%s' % (name, user))
    try:
        name = data['geonames'][0]['name']
    except IndexError:
        return None, None, None, None
    country = data['geonames'][0]['countryName']
    lat = data['geonames'][0]['lat']
    lng = data['geonames'][0]['lng']
    return name, country, lat, lng


@hook(cmds=['weather'], ex='weather Eaton Rapids, Michigan', args=True)
def weather(code, input):
    """weather <city, state|country|zip> - Return weather results for specified address"""
    # Here, we check if it's an actual area, if the geo returns the lat/long
    # then it is..
    name, country, lat, lng = location(input.group(2))
    if not name or not country or not lat or not lng:
        return code.reply('{red}{b}Incorrect location. Please try again!')
    try:
        data = web.json(api_uri % (api_key, lat, lng))['currently']
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
            output.append('{b}{blue}%s%s{b}{c}' %
                          (data['temperature'], degree))
        else:
            output.append('{b}{blue}%s%s{b}{c} ({b}{blue}%s%s{b}{c})' % (
                data['temperature'], degree, data[
                    'apparentTemperature'], degree
            ))
    if 'precipIntensity' in data and 'precipType' in data and 'precipIntensity' in data:
        # Nothing happening
        if data['precipIntensity'] == 0 and 'precipProbability' in data:
            # If probability above 0%
            if data['precipProbability'] != '0':
                output.append('{b}{blue}%s\%{b}{blue} chance of {b}{blue}%s{b}{c}' % (
                    data['precipProbability'], data['precipType']
                ))
        # Pricipitation
        else:
            output.append('{b}{blue}%s{b}{c} of {b}{blue}%s{b}{c}' % (
                data['precipType'], data['precipIntensity']
            ))
    if 'dewPoint' in data:
        output.append('{b}{blue}Dew:{b}{c} %s%s' % (data['dewPoint'], degree))
    if 'humidity' in data:
        output.append('{b}{blue}Humidity:{b}{c} %s' % data['humidity'])
    if 'windSpeed' in data:
        output.append('{b}{blue}Wind speed:{b}{c} %smph ({b}{blue}Bearing %s%s{b}{c})' % (
            data['windSpeed'], data['windBearing'], degree))
    if 'visibility' in data:
        output.append('{b}{blue}Visibility{b}{c} %s' % data['visibility'])
    if 'cloudCover' in data:
        output.append('{b}{blue}Cloud cover:{b}{c} %s' % data['cloudCover'])
    if 'pressure' in data:
        output.append('{b}{blue}Pressure{b}{c} %s' % data['pressure'])
    if 'ozone' in data:
        output.append('{b}{blue}Ozone level:{b}{c} %s' % data['ozone'])
    code.say(' | '.join(output))
