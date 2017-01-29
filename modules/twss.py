import re
from util.hook import *
from util import output
from util import database
from util import web

# Globals
enabled = False
db = []


def setup(code):
    # Read the databases here, make global variables. If we can't read the db
    #   then we need to disable the module..
    global enabled
    global db
    # Try to read the db...
    db = database.get(code.default, 'twss')
    if not db:
        try:
            db = web.json('https://static.liam.sh/code/twss.json')['lines']
            database.set(code.default, db, 'twss')
            output.info('Downloaded "That\'s What She Said" library and saved')
        except:
            output.error((
                'Failed to download "That\'s What She Said" library. '
                'Disabling twss.py.'
            ))
    if db:
        enabled = True


@hook(rule=r'.*', priority='low')
def twss(code, input):
    if not enabled:
        return
    # Check if what they said is in the database
    if re.sub('[^\w\s]', '', input.group().lower()) in db:
        return code.say('That\'s what she said.')
