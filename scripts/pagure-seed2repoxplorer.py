#!/usr/bin/env python

import os
import sys
import yaml
import shutil
import argparse
import requests
import subprocess

SEED='https://src.fedoraproject.org/lookaside/git-seed-latest.tar.xz'
DESTDIR='/var/lib/pagure-seed/'

def download_file(url, destdir):
    local_filename = url.split('/')[-1]
    local_filename = os.path.join(destdir, local_filename)
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        shutil.copyfileobj(r.raw, f)

    return local_filename

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Pagure 2 repoXplorer tool')
    parser.add_argument(
        '--refresh', action='store_true', default=False,
        help='Refresh seed on the local FS')
    parser.add_argument(
        '--yaml-path', default=os.path.join(DESTDIR, 'fedora-distgit.yaml'),
        help='Output YAML file path')

    args = parser.parse_args()
    repos_path = os.path.join(DESTDIR, 'git-checkout')

    if args.refresh:
        print('Downloading %s in %s ...' % (SEED, DESTDIR))
        seed_path = download_file(SEED, DESTDIR)
        print('Deflating %s ...' % seed_path)
        subprocess.call(
            ['xz', '-d', seed_path])
        ex_seed_path = seed_path.replace('.xz', '')
        print('Extracting %s in %s ...' % (ex_seed_path, DESTDIR))
        subprocess.call(
            ['tar', '-xf', ex_seed_path,
             '-C', os.path.dirname(DESTDIR)])
        print('Deleting %s' % ex_seed_path)
        os.unlink(ex_seed_path)

    repos = {}

    struct = {
        'groups': {
            'Fedora-bots': {
                 'description': 'Bots used by the Fedora project',
                 'emails': {
                     'releng@fedoraproject.org': {},
                     'rel-eng@lists.fedoraproject.org': {},
                 }
            }
        },
        'project-templates': {
            'Fedora Distgits template': {
                'uri': 'file://' + repos_path + '/%(name)s',
                'branches': ['master'],
                'gitweb': 'https://src.fedoraproject.org/rpms/%(name)s/c/%%(sha)s',
                'releases': [
                    {'name': 'Fedora 31', 'date': '2019-10-22'},
                    {'name': 'Fedora 30', 'date': '2019-04-30'},
                    {'name': 'Fedora 29', 'date': '2018-10-30'},
                    {'name': 'Fedora 28', 'date': '2018-05-01'},
                    {'name': 'Fedora 27', 'date': '2017-11-14'},
                    {'name': 'Fedora 26', 'date': '2017-07-11'},
                    {'name': 'Fedora 25', 'date': '2016-11-22'},
                    {'name': 'Fedora 24', 'date': '2016-06-21'},
                    {'name': 'Fedora 23', 'date': '2015-11-03'},
                    {'name': 'Fedora 22', 'date': '2015-05-26'},
                    {'name': 'Fedora 21', 'date': '2014-12-09'},
                    {'name': 'Fedora 20', 'date': '2013-12-17'},
                ],
                'index-tags': False
            }
        },
        'projects': {
            'Fedora Distgits': {
                'description': 'The Fedora project - Distgit repositories',
                'meta-ref': True,
                'bots-group': 'Fedora-bots',
                'repos': repos
            }
        }
    }

    print('Reading %s ...' % repos_path)
    _repos = [i for i in os.listdir(repos_path)
              if os.path.isdir(os.path.join(repos_path, i))]

    print('Building in-memory YAML ...')
    for r in _repos:
        repos.update({r: {'template': 'Fedora Distgits template'}})

    print('Dumping in %s' % args.yaml_path)
    with open(args.yaml_path, 'w') as fd:
        fd.write(yaml.safe_dump(struct,
                                default_flow_style=False))

    print('Yaml wrote in %s' % args.yaml_path)
