import os
import pyalpm
from types import SimpleNamespace
from lilaclib import *

g = SimpleNamespace()

def _download_official_pkgbuild_trunk(name: str) -> List[str]:
  url = 'https://archlinux.org/packages/search/json/?name=' + name
  logger.info('download PKGBUILD for %s.', name)
  info = s.get(url).json()
  r = [r for r in info['results'] if r['repo'] != 'testing'][0]
  repo = r['repo']
  if repo in ('core', 'extra'):
    gitrepo = 'packages'
  else:
    gitrepo = 'community'
  pkgbase = [r['pkgbase'] for r in info['results'] if r['repo'] != 'testing'][0]

  tarball_url = 'https://github.com/archlinux/svntogit-%s/archive/refs/heads/packages/%s.tar.gz' % (gitrepo, pkgbase)
  logger.debug('downloading Arch package tarball from: %s', tarball_url)
  tarball = s.get(tarball_url).content
  path = f'svntogit-{gitrepo}-packages-{pkgbase}/trunk'
  files = []

  with tarfile.open(
    name=f"{pkgbase}.tar.gz", mode="r:gz", fileobj=io.BytesIO(tarball)
  ) as tarf:
    for tarinfo in tarf:
      dirname, filename = os.path.split(tarinfo.name)
      if dirname != path:
        continue
      tarinfo.name = filename
      logger.debug('extract file %s.', filename)
      tarf.extract(tarinfo)
      files.append(filename)

  return files

def pre_build():
    g.files = _download_official_pkgbuild_trunk('linux-zen')

    run_protected(['patch', '-N', 'config', 'config.patch' ])

    for line in edit_file('PKGBUILD'):
        if line.startswith('pkgbase='):
            line = "pkgbase=linux-zen-znver3"
        elif line.startswith('pkgname=('):
            line = line.replace('"$pkgbase-docs"', '')
        elif line.startswith('pkgver='):
            line = line + '\n_cjkver=6.0'
        elif line.startswith('source=('):
            line = line.replace('source=(', (
                'source=(\n' +
                '"cjktty.patch::https://github.com/zhmars/cjktty-patches/raw/master/v${_cjkver%.*}.x/cjktty-${_cjkver}.patch"\n' +
                '"https://github.com/zhmars/cjktty-patches/raw/master/cjktty-add-cjk32x32-font-data.patch"\n'
            ))
        elif line.startswith('sha256sums=('):
            line = line.replace(
                'sha256sums=(',
                'sha256sums=(SKIP\nSKIP\n'
            )
        elif 'make htmldocs all' in line:
            line = 'make all'
        print(line)

    pkgver, _ = get_pkgver_and_pkgrel()
    if pyalpm.vercmp(_G.newver, pkgver) > 0:
        update_pkgver_and_pkgrel(_G.newver, updpkgsums=True)
    else:
        run_protected(["updpkgsums"])

    g.files.append('cjktty.patch')
    g.files.append('cjktty-add-cjk32x32-font-data.patch')


def post_build():
    git_add_files(g.files)
    git_commit()
