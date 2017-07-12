#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import bz2
import logging
import fnmatch
import os
import pprint
from os import path
import sys

import collections
import unicodecsv as csv
try:
    import ujson as json
except ImportError:
    import json


logger = logging.getLogger(__name__)


def main():
    categories_map = {}
    counter = collections.Counter()

    matches = []
    for root, dirnames, filenames in os.walk(sys.argv[2]):
        for filename in fnmatch.filter(filenames, '*'):
            matches.append(os.path.join(root, filename))

    for filepath in matches:
        csvfile = open(filepath, 'rb')

        # TODO: csv module has problems with null bytes?
        reader = csv.reader(csvfile, encoding='utf-8')
        next(reader, None)  # skip the headers

        try:
            for row in reader:
                category_name = row[1].replace("Category:", "")
                if category_name not in categories_map:
                    categories_map[category_name] = []
                categories_map[category_name].append(path.basename(filepath))
        except csv.Error as ce:
            logger.warning('DECODE FAIL: %s %s', filepath, ce.message)
            pass
        csvfile.close()

    wfilepath = sys.argv[1]
    if wfilepath.endswith(".bz2"):
        wfile = bz2.BZ2File(wfilepath)
    else:
        wfile = open(wfilepath, 'rb')
    for line in wfile:
        data = json.loads(line)
        if 'categories' not in data:
            logger.warning('NO CATEGORIES FOR: %s', data['title'])
            counter.update(["NO_CATEGORY"])
            continue
        article_categories = data['categories']
        for cat in article_categories:
            try:
                topical_categories = categories_map[cat]
                counter.update(topical_categories)
            except KeyError as ke:
                logger.warning('COULD NOT FIND TOPICS FOR: %s', cat)
                counter.update(["NO_TOPIC"])

    pprint.pprint(counter)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    main()