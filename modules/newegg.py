from util import web
from util.hook import *

item_info = 'http://www.ows.newegg.com/Products.egg/%s/ProductDetails'
item_re = r'.*(?:www.newegg.com|newegg.com)/Product/Product\.aspx\?.*?Item=([-_a-zA-Z0-9]+).*'


@hook(rule=item_re)
def newegg(code, input):
    """ Automatically find the information from a newegg url and display it
       to users in a channe """
    id = str(input.group(1))

    try:
        data = web.json(item_info % id)
    except:
        return  # Same as below
    if not data:
        return  # We had issues.. ignore

    if len(data['Title']) > 50:
        title = ' '.join(data['Title'][:50].split()[0:-1]) + '...'
    else:
        title = data['Title']
    title = '{b}%s{b}' % title

    if not data['FinalPrice'] == data['OriginalPrice']:
        price = '{b}%s{b} (was {b}%s{b})' % (
            data['FinalPrice'], data['OriginalPrice'])
    else:
        price = '{b}' + data['FinalPrice'] + '{b}'

    review_count = data['ReviewSummary']['TotalReviews']
    review = data['ReviewSummary']['Rating']
    if not review_count == '[]':
        if review_count[1:-1] == '1':
            rating_fmt = 'rating'
        else:
            rating_fmt = 'ratings'
        rating = 'Rated {b}%s/5{b} ({b}%s %s{b})' % (review,
                                                     review_count[1:-1], rating_fmt)
    else:
        rating = '{b}No Ratings{b}'

    tags = []

    if data['IsFeaturedItem']:
        tags.append('{b}{blue}Featured{c}{b}')

    if data['Instock']:
        tags.append('{b}{green}In Stock{c}{b}')
    else:
        tags.append('{b}{red}Out Of Stock{c}{b}')

    if data['FreeShippingFlag']:
        tags.append('{b}{green}Free Shipping{c}{b}')

    if data['IsShellShockerItem']:
        tags.append(u'{b}{green}Shell Shocker{c}{b}')

    tags = ', '.join(tags)

    return code.say(' - '.join([title, price, rating, tags]))
