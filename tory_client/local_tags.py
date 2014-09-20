# vim:fileencoding=utf-8

import json
import os

from codecs import open


DEFAULT_HOST_TAGS_FILES = (
    '/etc/host-tags.json',
    '/usr/local/etc/host-tags.json',
    'host-tags.json'
)


def load_local_tags(files=DEFAULT_HOST_TAGS_FILES):
    tagdict = {}
    for filename in files:
        if not os.path.exists(filename):
            continue
        with open(filename) as infile:
            tagdict.update(json.load(infile))

    return [[str(key), str(value)] for key, value in tagdict.items()]
