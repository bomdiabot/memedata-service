#!/usr/bin/env python3

from service.database import session as db
from service.models import Text, Tag
import uuid
import random

def get_rand_str():
    size = random.randint(0, 1000) % 16
    return str(uuid.uuid4())[:size]

def get_tag():
    return Tag(get_rand_str())

def get_text():
    return Text(get_rand_str())

def main():
    n_tags = random.randint(100, 200)
    n_texts = random.randint(300, 600)

    tags = [get_tag() for __ in range(n_tags)]
    texts = [get_text() for __ in range(n_texts)]

    db.add_all(tags)
    db.add_all(texts)
    db.commit()

if __name__ == '__main__':
    main()
