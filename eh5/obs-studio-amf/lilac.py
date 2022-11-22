from types import SimpleNamespace
from lilaclib import *

g = SimpleNamespace()


def pre_build():
    g.files = download_official_pkgbuild('obs-studio')

    hasPrepare = False
    patchLines = (
        'pushd $__pkgname-$pkgver\n' +
        'patch -Np1 < "$srcdir"/7206.patch\n' +
        'popd'
    )

    for line in edit_file('PKGBUILD'):
        if line.startswith('pkgname='):
            line = (
                'pkgname=obs-studio-amf\n' +
                '__pkgname=obs-studio\n' +
                'conflicts=(obs-studio)'
            )
        elif 'pkgname' in line:
            line = line.replace('pkgname', '__pkgname')

        if line.startswith('pkgver='):
            line = (
                line +
                '\n__ver=${pkgver%%.*}\n' +
                'provides=(obs-studio=$__ver)'
            )
        elif line.startswith('source=('):
            line = line.replace('source=(', 'source=(7206.patch\n')
        elif line.startswith('sha256sums=('):
            line = line.replace(
                'sha256sums=(',
                'sha256sums=(87bc6bab3492002cd6aec54136b0374c98a407e5a359e1bdd3d71ca6729619b0\n'
            )
        elif line.startswith('prepare()'):
            hasPrepare = True
            line = line + '\n' + patchLines

        print(line)

    if not hasPrepare:
        print('\nprepare() {\n' + patchLines + '\n}')


def post_build():
    git_add_files(g.files)
    git_commit()
