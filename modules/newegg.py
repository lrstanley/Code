from util import web
from util.hook import *

item_info = 'http://www.ows.newegg.com/Products.egg/%s/Detail'
item_re = r'.*(?:www.newegg.com|newegg.com)/Product/Product\.aspx\?.*?Item=([-_a-zA-Z0-9]+).*'


headers = {
    'User-Agent': 'Newegg Android App / 4.5.0',
    'Referer': 'http://www.newegg.com/'
}


@hook(rule=item_re)
def newegg(code, input):
    """ Automatically find the information from a newegg url and display it
       to users in a channel """
    id = str(input.group(1))

    try:
        data = web.json(item_info % id, headers=headers)
    except Exception as e:
        return  # Same as below
    if not data or not data.get('Basic'):
        return  # We had issues.. ignore

    if len(data['Basic'].get('Title', '')) > 50:
        title = ' '.join(data['Basic']['Title'][:50].split()[0:-1]) + '...'
    else:
        title = data['Basic']['Title']
    title = '{b}%s{b}' % title

    if not data['Basic']['FinalPrice'] == data['Basic']['OriginalPrice']:
        price = '{b}%s{b} (was {b}%s{b})' % (
            data['Basic']['FinalPrice'], data['Basic']['OriginalPrice'])
    else:
        price = '{b}' + data['Basic']['FinalPrice'] + '{b}'

    review_count = data['Basic']['ReviewSummary']['TotalReviews']
    review = data['Basic']['ReviewSummary']['Rating']
    if not review_count == '[]':
        if review_count == '1':
            rating_fmt = 'rating'
        else:
            rating_fmt = 'ratings'
        rating = 'Rated {b}%s/5{b} ({b}%s %s{b})' % (review, review_count, rating_fmt)
    else:
        rating = '{b}No Ratings{b}'

    tags = []

    if data['Basic']['IsFeaturedItem']:
        tags.append('{b}{blue}Featured{c}{b}')

    if data['Basic']['Instock']:
        tags.append('{b}{green}In Stock{c}{b}')
    else:
        tags.append('{b}{red}Out Of Stock{c}{b}')

    if data['Basic']['IsFreeShipping']:
        tags.append('{b}{green}Free Shipping{c}{b}')

    tags = ', '.join(tags)

    return code.say(' - '.join([title, price, rating, tags]))
