#!/usr/bin/env python3

import argparse

from memedata.app import get_app
from memedata.database import db
import memedata.config as config

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reset_db",
        nargs="?",
        help="reset database",
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

if __name__ == '__main__':
    main()
