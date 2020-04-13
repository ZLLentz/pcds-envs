import argparse
import configparser
import contextlib
import json
import os
import requests
import subprocess
from pathlib import Path

URL_BASE = 'https://github.com/{}.git'
parser = argparse.ArgumentParser()
parser.add_argument('env')
parser.add_argument('--tag', action='store_true')


def version_info():
    conda_list = subprocess.check_output(['conda', 'list', '--json'],
                                         universal_newlines=True)
    info_list = json.loads(conda_list)
    version_dict = {}

    for item in info_list:
        version_dict[item['name']] = item['version']

    return version_dict


def setup_all_tests(repo_file, tags=None):
    url_base = 'https://github.com/{}.git'
    repo_file = Path(repo_file)

    with repo_file.open('r') as fd:
        repos = fd.read().strip().splitlines()

    for repo in repos:
        pkg = repo.split('/')[-1]
        if tags is None:
            setup_one_test(repo, pkg)
        else:
            try:
                tag = tags[pkg]
            except KeyError as err:
                msg = f'Did not find package {pkg} in environment'
                raise RuntimeError(msg) from err
            setup_test(repo, pkg, tag=tags[pkg])


def setup_one_test(repo, pkg, tag=None):
    url = URL_BASE.format(repo)
    try:
        subprocess.run(['git', 'clone', '--recursive', url, '--depth', '1'],
                       check=True)
    except subprocess.CalledProcessError as err:
        raise RuntimeError(f'Error cloning from {url}') from err

    if tag is not None:
        print('Checking out package tag')
        with pushd(pkg):
            config = configparser.ConfigParser()
            config.read('setup.cfg')
            try:
                tag_prefix = config['versioneer']['tag_prefix']
            except KeyError:
                tag_prefix = ''
            try:
                subprocess.run(['git', 'fetch', '--tags'], check=True)
                subprocess.run(['git', 'checkout', tag_prefix + tag],
                               check=True)
            except KeyError as err:
                raise ValueError(f'Did not have tag for {pkg}') from err
            except subprocess.CalledProcessError as err:
                raise RuntimeError(f'Error checking out tag') from err


@contextlib.contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    yield
    os.chdir(previous_dir)


def main():
    print('Running pcds-envs test setup')
    args = parser.parse_args()

    pcds_envs = Path(__file__).resolve().parent.parent
    repo_file = pcds_envs / 'envs' / args.env / 'package-tests.txt'

    if args.tag:
        tags = version_info()

        if len(tags) == 0:
            print('No packages in current environment to test, quitting')
    else:
        tags = None

    setup_all_tests(repo_file, tags=tags)


if __name__ == '__main__':
    main()
