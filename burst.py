# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'site-packages'))

from burst.burst import search

import pprint

def search_movie(payload):
    return search(payload, 'movie')


def search_season(payload):
    return search(payload, 'season')


def search_episode(payload):
    return search(payload, 'episode')

#pp = pprint.PrettyPrinter(width=41, compact=True)
#res = search_movie({"title": "Avangers End Game", "titles": {}, "year": "2019"})
#res = search_episode({"title": "Silicon Valley", "titles": {}, "year": "2019", "season": 6, "episode": 6})
#pp.pprint(res)