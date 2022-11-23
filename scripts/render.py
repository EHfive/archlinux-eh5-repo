#!/usr/bin/env python3
import os
import sys

# autopep8: off
dirname = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(dirname, '../3rdparty/chevron'))
import chevron
# autopep8: on


def render(templateDir, destDir, data):
    import shutil
    for root, _, files in os.walk(templateDir):
        relpath = os.path.relpath(root, templateDir)
        destRoot = os.path.join(destDir, relpath)
        os.makedirs(destRoot, exist_ok=True)

        for filename in files:
            dest = None
            basename, ext = os.path.splitext(filename)
            if ext == '.mustache':
                res = None
                dest = os.path.join(destRoot, basename)
                with open(os.path.join(root, filename)) as f:
                    res = chevron.render(f.read(), data)
                with open(dest, 'w') as f:
                    f.write(res)
            else:
                dest = os.path.join(destRoot, filename)
                shutil.copyfile(os.path.join(root, filename), dest)
            print(os.path.normpath(dest))


if __name__ == '__main__':
    import json
    if len(sys.argv) < 4:
        print("usage: python render.py <data.json> <template dir> <dest dir>")
        exit(1)
    preset = sys.argv[1]
    templateDir = sys.argv[2]
    destDir = sys.argv[2]

    with open(os.path.join(dirname, preset)) as f:
        render(templateDir, destDir, json.loads(f.read()))
