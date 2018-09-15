#!/usr/bin/env python3

import yaml
import os
import argparse

DEF_SETUP_FILE_PATH = './setup.yml'
PREFIX = 'MEMEDATA_'
ENVS = {'production', 'development'}

def get_env_key(key):
    return '{}{}'.format(PREFIX, key.upper())

def get_env_dict(setup, gen_secrets=True):
    dct = {}
    #setting up general args
    keys = set(setup.keys()) - {'production', 'development', 'test'}
    for k in keys:
        dct[get_env_key(k)] = setup[k]
    #setting specific env/test vars
    for k in ['host', 'port', 'db_path']:
        dct[get_env_key(k)] = setup[setup['env']][k]
        dct[get_env_key('test_' + k)] = setup['test'][k]
    #setting secret keys
    if gen_secrets:
        dct[get_env_key('secret_key')] = os.urandom(32).hex()
        dct[get_env_key('jwt_secret_key')] = os.urandom(32).hex()
    return dct

def get_env_file_lines(dct):
    lines = []
    #lines.append('#!/usr/bin/bash')
    lines.extend('export {}={}'.format(k, v) for k, v in dct.items())
    return lines

def dump_env_file_lines(lines):
    return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'setup_file',
        help='setup YAML file (default={})'.format(DEF_SETUP_FILE_PATH),
        nargs='?',
        default=DEF_SETUP_FILE_PATH,
    )
    parser.add_argument(
        '--env',
        help='environment to set (overrides setup file)',
        default=''
    )
    parser.add_argument(
        '--dst_file',
        help='destiny file to save (prints to stdout if not given)',
        default='',
    )
    parser.add_argument(
        '--no_secrets',
        help='do not generate secret keys',
        nargs='?',
        const=True,
        default=False,
    )
    args = parser.parse_args()

    with open(args.setup_file) as f:
        setup = yaml.load(f)

    if args.env:
        setup['env'] = args.env
    elif setup.get('env') is None:
        raise ValueError('must specify env either via setup file or via cli')
    assert setup['env'] in ENVS

    dct = get_env_dict(setup, not args.no_secrets)
    lines = get_env_file_lines(dct)
    dump = dump_env_file_lines(lines)

    if args.dst_file:
        with open(args.dst_file, 'w') as f:
            print(dump, file=f)
        print('env file saved to \'{}\''.format(args.dst_file))
    else:
        print(dump)

if __name__ == '__main__':
    main()
