#!/usr/bin/env python3
from render import render
import os
import sys
from lilaclib import parse_document_from_requests, s

dirname = os.path.dirname(os.path.realpath(__file__))


def get_aur_packager(name: str):
    doc = parse_document_from_requests(
        f'https://aur.archlinux.org/pkgbase/{name}', s)
    maintainer_cell = doc.xpath(
        '//th[text()="Maintainer:"]/following::td[1]')[0]
    maintainer = maintainer_cell.text_content().strip().split(None, 1)[0]
    last_packager_cell = doc.xpath(
        '//th[text()="Last Packager:"]/following::td[1]')[0]
    last_packager = last_packager_cell.text_content().strip()

    if  last_packager == 'lilac':
        return maintainer
    return last_packager


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python initpkg.py <pkgbase> [<template>]')
    pkgbase = sys.argv[1]
    template = 'aur'
    if len(sys.argv) > 2:
        template = sys.argv[2]

    baseDir = os.path.join(dirname, '../eh5', pkgbase)
    templateDir = os.path.join(dirname, '../templates', template)

    maintainer = None
    if template == 'aur':
        maintainer = get_aur_packager(pkgbase)

    render(templateDir, baseDir, {'pkgbase': pkgbase, 'maintainer': maintainer})
