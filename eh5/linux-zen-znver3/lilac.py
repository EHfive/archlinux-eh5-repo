import os
import pyalpm
from types import SimpleNamespace
from lilaclib import *

g = SimpleNamespace()


def download_latest_pkgbuild(name: str) -> list[str]:
    url = 'https://archlinux.org/packages/search/json/?name=' + name
    logger.info('download PKGBUILD for %s.', name)
    info = s.get(url).json()
    pkgbase = [r['pkgbase'] for r in info['results']][0]

    tarball_url = 'https://gitlab.archlinux.org/archlinux/packaging/packages/{0}/-/archive/main/{0}-main.tar.bz2'.format(
        pkgbase)
    logger.debug('downloading Arch package tarball from: %s', tarball_url)
    tarball = s.get(tarball_url).content
    path = f'{pkgbase}-main'
    files = []

    with tarfile.open(
        name=f"{pkgbase}-main.tar.bz2", fileobj=io.BytesIO(tarball)
    ) as tarf:
        for tarinfo in tarf:
            dirname, filename = os.path.split(tarinfo.name)
            if dirname != path:
                continue
            if filename in ('.SRCINFO', '.gitignore'):
                continue
            tarinfo.name = filename
            logger.debug('extract file %s.', filename)
            tarf.extract(tarinfo)
            files.append(filename)

    return files


def pre_build():
    g.files = download_latest_pkgbuild('linux-zen')

    run_protected(['patch', '-N', 'config', 'config.patch'])

    doc_deps = [
        'graphviz',
        'imagemagick',
        'python-sphinx',
        'texlive-latexextra'
    ]

    for line in edit_file('PKGBUILD'):
        if line.startswith('pkgbase='):
            line = "pkgbase=linux-zen-znver3"
        elif '"$pkgbase-docs"' in line:
            line = line.replace('"$pkgbase-docs"', '')
        # elif line.startswith('pkgver='):
        #     line = line + '\n_cjkver=6.3'
        elif line.startswith('source=('):
            line = line.replace('source=(', (
                'source=(\n' +
                # '"cjktty.patch::https://github.com/zhmars/cjktty-patches/raw/master/v${_cjkver%.*}.x/cjktty-${_cjkver}.patch"\n' +
                # '"https://github.com/zhmars/cjktty-patches/raw/master/cjktty-add-cjk32x32-font-data.patch"\n'
                'pahole-use-llvm-objcopy.patch\n'
            ))
        elif line.startswith('b2sums=('):
            line = line.replace(
                'b2sums=(',
                # 'b2sums=(SKIP\nSKIP\n'
                'b2sums=(SKIP\n'
            )
        elif line.startswith('makedepends=('):
            line = line.replace('makedepends=(', 'makedepends=(llvm ')
        elif line.startswith('validpgpkeys'):
            line = line.replace('validpgpkeys', '_validpgpkeys')
        elif line.startswith('sha256sums'):
            line = line.replace('sha256sums', '_sha256sums')
        elif 'make htmldocs' in line:
            line = ''
        else:
            for dep in doc_deps:
                if dep in line:
                    line = line.replace(dep, '')

        print(line)

    pkgver, _ = get_pkgver_and_pkgrel()
    if False and pyalpm.vercmp(_G.newver, pkgver) > 0:
        update_pkgver_and_pkgrel(_G.newver, updpkgsums=True)
    else:
        run_protected(["updpkgsums"])

    g.files.append('cjktty.patch')
    g.files.append('cjktty-add-cjk32x32-font-data.patch')


def post_build():
    git_add_files(g.files)
    git_commit()
