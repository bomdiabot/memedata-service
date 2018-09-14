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

def main():
    parser = argparse.ArgumentParser()
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
    args = parser.parse_args()

    #app setup
    app = get_app(config.SetupConfig)
    #database setup
    if args.reset_db:
        print('dropping tables...', end=' ', flush=True)
        with app.app_context():
            db.drop_all()
        print('done.')

    print('creating tables...', end=' ', flush=True)
    with app.app_context():
        db.create_all()
    print('done.')

    if args.create_su:
        passwd = get_pass('enter superuser password: ')
        with app.app_context():
            User.create_and_save('su', passwd)
        print('superuser "su" created.')

    print('all done.')

if __name__ == '__main__':
    main()
