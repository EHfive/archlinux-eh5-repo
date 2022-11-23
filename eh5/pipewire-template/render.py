#!/usr/bin/env python3
import os
import sys

# autopep8: off
dirname = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(dirname, '../../scripts'))
from render import render
# autopep8: on

if __name__ == '__main__':
    import json
    preset = 'common.json'
    destDir = os.getcwd()
    if len(sys.argv) > 1:
        preset = sys.argv[1]
    if len(sys.argv) > 2:
        destDir = sys.argv[2]

    base = os.path.join(dirname, 'template')
    with open(os.path.join(dirname, preset)) as f:
        render(base, destDir, json.loads(f.read()))
