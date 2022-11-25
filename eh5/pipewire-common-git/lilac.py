import os
from types import SimpleNamespace
from lilaclib import *

dirname = os.path.dirname(os.path.realpath(__file__))
g = SimpleNamespace()

build_prefix = 'extra-x86_64'


def pre_build():
    res = run_cmd([
        'python',
        os.path.join(dirname, '../pipewire-template/render.py'),
        'common.json',
        dirname
    ])
    g.files = res.splitlines()


def post_build():
    git_add_files(g.files)
    git_commit()
    update_aur_repo()


if __name__ == '__main__':
    single_main()
