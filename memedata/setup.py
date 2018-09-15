#!/usr/bin/env python3

import argparse
import getpass

from memedata.app import get_app
from memedata.database import db
from memedata.models import User
import memedata.config as config

def get_pass(prompt, max_n_trials=3):
    for i in range(max_n_trials):
        pass_1 = getpass.getpass(prompt)
        if len(pass_1) < config.min_password_len:
            print('passw too short (min = {})'.format(config.min_password_len))
            continue
        pass_2 = getpass.getpass('enter again: ')
        if pass_1 != pass_2:
            print('passwords differ, try again')
            continue
        return pass_1
    raise ValueError('maximum number of trials reached')

def create_db_tables(app):
    with app.app_context():
        db.create_all()

def drop_db_tables(app):
    with app.app_context():
        db.drop_all()

def del_db(app):
    drop_db_tables(app)

def create_db(app):
    create_db_tables(app)

def reset_db(app):
    drop_db_tables(app)
    create_db_tables(app)

def create_su(app, passwd=''):
    if not passwd:
        passwd = get_pass('enter superuser password: ')
    elif len(passwd) < config.min_password_len:
        raise ValueError(
            'length of password < {}'.format(config.min_password_len))
    with app.app_context():
        User.create_and_save('su', passwd)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--create_db',
        nargs='?',
        help='create database',
        const=True,
        default=False
    )
    parser.add_argument(
        '--del_db',
        nargs='?',
        help='delete database',
        const=True,
        default=False
    )
    parser.add_argument(
        '--reset_db',
        nargs='?',
        help='reset database',
        const=True,
        default=False
    )
    parser.add_argument(
        '--create_su',
        nargs='?',
        help='create superuser with name "su"',
        const=True,
        default=False
    )
    parser.add_argument(
        '--su_passwd',
        help='superuser password (leave empty to be prompted)',
        default='',
    )
    args = parser.parse_args()

    #app setup
    app = get_app()

    print('setting up for env "{}"'.format(config.env))
    #database setup
    if args.reset_db:
        print('resetting database...', end=' ', flush=True)
        reset_db(app)
        print('done.')
    elif args.create_db:
        print('creating tables...', end=' ', flush=True)
        create_db(app)
        print('done.')
    elif args.del_db:
        print('deleting database...', end=' ', flush=True)
        del_db(app)
        print('done.')

    if args.create_su:
        create_su(app, args.su_passwd)
        print('superuser "su" created.')

    print('all done.')

if __name__ == '__main__':
    main()
