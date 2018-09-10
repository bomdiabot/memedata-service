#!/usr/bin/env python3

from memedata.app import get_app
from memedata.database import db
from memedata.models import Text, Tag
import uuid
import random
import os

SENTENCES_FILES = [
    os.path.join('data', 'sentences.txt'),
]

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

def populate_texts_with_sentences():
    for path in SENTENCES_FILES:
        with open(path) as f:
            lines = [l.strip() for l in f]
        texts = [Text(l) for l in lines if l]
        with get_app().app_context():
            db.session.add_all(texts)
            db.session.commit()

def populate_tags(size):
    texts = [get_tag() for __ in range(size)]
    with get_app().app_context():
        db.session.add_all(texts)
        db.session.commit()

def sample(iterable, n):
    return random.sample(iterable, min(n, len(iterable)))

def assign_texts_tags(max_n_tags=10):
    with get_app().app_context():
        texts = Text.query.all()
        tags = Tag.query.all()
        for text in texts:
            tags_ = sample(tags, random.randint(0, max_n_tags))
            text.tags.extend(tags_)
        db.session.add_all(texts)
        db.session.commit()

def main():
    print('populating texts...')
    populate_texts_with_sentences()
    populate_texts(random.randint(50, 100))
    print('populating tags...')
    populate_tags(random.randint(100, 150))
    print('assigning tags to texts...')
    assign_texts_tags()
    print('done')

if __name__ == '__main__':
    main()
