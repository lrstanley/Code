import os
import json


db_name = '%s.data.db'
mod_name = '%s.module.%s.db'


def get(bot, module=False):
    """ get(code.default, modulename) """
    if module:
        fn = mod_name % (bot, str(module))
    else:
        fn = db_name % bot
    module_filename = os.path.join(os.path.expanduser('~/.code'), fn)
    if not os.path.exists(module_filename):
        return False
    with open(module_filename, 'r') as f:
        try:
            data = json.loads(f.read())
            if 'list' in data:
                data = data['list']
        except ValueError:
            data = str(f.read())
    return data


def set(bot, data, module=False):
    """ set(code.default, {}, modulename) """
    if module:
        fn = mod_name % (bot, str(module))
    else:
        fn = db_name % bot
    module_filename = os.path.join(os.path.expanduser('~/.code'), fn)
    with open(module_filename, 'w') as f:
        if isinstance(data, dict):
            f.write(json.dumps(data))
        elif isinstance(data, list):
            f.write(json.dumps({'list': data}))
        else:
            f.write(str(data))
    return True
