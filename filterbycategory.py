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
    topics_for = {}
    topics_counter = collections.Counter()

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
                if category_name not in topics_for:
                    topics_for[category_name] = []
                topics_for[category_name].append(path.basename(filepath))
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
        article = json.loads(line)
        if 'categories' not in article:
            logger.warning('NO CATEGORIES FOR: %s', article['title'])
            topics_counter.update(["NO_CATEGORY"])
            continue
        categories = article['categories']
        for cat in categories:
            num_topics = 0
            try:
                topics = topics_for[cat]
                topics_counter.update(topics)
                num_topics += len(topics)
            except KeyError:
                pass

        if num_topics == 0:
            logger.debug('COULD NOT FIND TOPICS FOR: %s', cat)
            topics_counter.update(["NO_TOPIC"])

    pprint.pprint(topics_counter.most_common())


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    main()