#!/usr/bin/env python
"""
Code Copyright (C) 2012-2014 Liam Stanley
database.py - Code Module Database Manager
http://code.liamstanley.io/
"""


import os
import json


name_management = 'module.%s.db'

def get(module):
    fn = name_management % str(module)
    module_filename = os.path.join(os.path.expanduser('~/.code'), fn)
    if not os.path.exists(module_filename):
        f = open(module_filename, 'w')
        f.write(json.dumps(dict()))
        f.close()
        return dict()
    else:
        f = open(module_filename, 'r')
        data = json.loads(f)
        return data

def set(module, data, pretty=False):
    if not isinstance(data, dict):
        return False
    fn = name_management % str(module)
    module_filename = os.path.join(os.path.expanduser('~/.code'), fn)
    if not os.path.exists(module_filename):
        f = open(module_filename, 'w')
        f.write(json.dumps(data, indent=pretty))
        f.close(json.dumps(data, indent=pretty))
        return True