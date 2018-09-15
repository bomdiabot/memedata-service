#!/usr/bin/env python3

import os
import uuid
import yaml
import subprocess
import sys
import argparse

DEF_SETUP_FILE_PATH = 'setup.yml'

TESTS_DIR_PATH = './tests'

RUN_MODES = [
    'setup',
    'server',
    'populate_db',
    'test',
]

ENVS = [
    'development',
    'production',
]

def export_runtime_env_vars(conf, mode, env=None):
    env = 'test' if mode == 'test' else env
    env_conf = conf[env]
    os.environ['MEMEDATA_ENV'] = env
    os.environ['MEMEDATA_DB_PATH'] = str(env_conf['db_path'])
    os.environ['MEMEDATA_HOST'] = str(env_conf['host'])
    os.environ['MEMEDATA_PORT'] = str(env_conf['port'])

def run(cmd, *args):
    cmd.extend(args)
    subprocess.run(cmd)

def setup_service(*args):
    run(['python3', '-m', 'memedata.setup'], *args)

def run_server(*args):
    os.environ['FLASK_APP'] = 'memedata.app:get_app'
    os.environ['FLASK_ENV'] = os.environ['MEMEDATA_ENV']
    port = os.environ['MEMEDATA_PORT']
    host = os.environ['MEMEDATA_HOST']
    run(['flask', 'run', '--host={}'.format(host), '--port={}'.format(port)],
        *args)

def populate_db(*args):
    run(['python3', 'populate_db.py'], *args)

def test(*args):
    if not args:
        args = [TESTS_DIR_PATH]
    run(['python3', '-m', 'pytest'], *args)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'mode',
        help='mode to be run',
        choices=RUN_MODES,
    )
    parser.add_argument(
        '--env',
        help='environment (ignored if mode=test)',
        choices=ENVS,
        default='production',
    )
    parser.add_argument(
        '--setup_path',
        help='setup YAML conf path',
        default=DEF_SETUP_FILE_PATH,
    )
    args, unknown = parser.parse_known_args()

    if not 'MEMEDATA_SECRET_KEY' in os.environ:
        raise ValueError('env not properly set')
    if not 'MEMEDATA_JWT_SECRET_KEY' in os.environ:
        raise ValueError('env not properly set')

    #setting up env
    with open(args.setup_path) as f:
        conf = yaml.load(f)
    export_runtime_env_vars(conf, args.mode, args.env)

    if args.mode == 'setup':
        setup_service(*unknown)
    elif args.mode == 'server':
        run_server(*unknown)
    elif args.mode == 'test':
        test(*unknown)
    elif args.mode == 'populate_db':
        populate_db(*unknown)
    else:
        raise ValueError(args.mode)

if __name__ == '__main__':
    main()
