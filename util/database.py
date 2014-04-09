#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
database.py - Code Module Database Manager
http://code.liamstanley.io/
"""


import os
import json


db_name = 'data.db'
mod_name = 'module.%s.db'


def get(module=False):
    if module:
        fn = mod_name % str(module)
    else:
        fn = db_name
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


def set(data, module=False):
    if module:
        fn = mod_name % str(module)
    else:
        fn = db_name
    module_filename = os.path.join(os.path.expanduser('~/.code'), fn)
    with open(module_filename, 'w') as f:
        if isinstance(data, dict):
            f.write(json.dumps(data))
        elif isinstance(data, list):
            f.write(json.dumps({'list': data}))
        else:
            f.write(str(data))
    return True
