from types import SimpleNamespace
from lilaclib import *

g = SimpleNamespace()

NAME = 'linux-firmware-strip-amdgpu'

def pre_build():
    g.files = download_official_pkgbuild('linux-firmware')

    in_pkgname = False
    in_package = False

    for line in edit_file('PKGBUILD'):
        if in_pkgname:
            if ')' in line:
                in_pkgname = False
            continue
        if in_package:
            if line.startswith('}'):
                in_package = False
                line = (
                    '_pick linux-firmware-amdgpu usr/lib/firmware/amdgpu\n' +
                    '}'
                )
        elif line.startswith('pkgname=('):
            in_pkgname = True
            line = f'pkgname=( {NAME} )'
        elif line.startswith('package_linux-firmware('):
            in_package = True
            line = (
                f'package_{NAME}() {{\n' +
                'provides=( linux-firmware )\n' +
                'conflicts=( linux-firmware )\n'
            )

        print(line)


def post_build():
    git_add_files(g.files)
    git_commit()
