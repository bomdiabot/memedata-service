#!/usr/bin/env python3

from memedata.app import get_app
from memedata.database import db
from memedata.models import Text, Tag
import uuid
import random

def get_rand_str(maxsize=16):
    size = random.randint(0, 10000) % maxsize
    return str(uuid.uuid4())[:size]

def get_tag():
    return Tag(get_rand_str(16))

def get_text():
    return Text(get_rand_str(64))

def populate_texts(size):
    texts = [get_text() for __ in range(size)]
    with get_app().app_context():
        db.session.add_all(texts)
        db.session.commit()

def populate_tags(size):
    texts = [get_tag() for __ in range(size)]
    with get_app().app_context():
        db.session.add_all(texts)
        db.session.commit()

def main():
    print('populating texts...')
    populate_texts(random.randint(500, 600))
    print('populating tags...')
    populate_tags(random.randint(100, 200))
    print('done')

if __name__ == '__main__':
    main()
