# -*- coding: utf-8 -*-
"""
Definitions and overrides loader
"""

from future.utils import PY3, iteritems

import os
import sys
import json
import logging
import time
import collections
from glob import glob
from urllib.parse import urlparse

start_time = time.time()
ADDON_PATH = "."

definitions = {}
mandatory_fields = {
    'name': '',
    'predefined': False,
    'enabled': False,
    'private': False,
    'id': '',
    'languages': '',
    'charset': 'utf8',
    'response_charset': None
}


def load_providers(path, custom=False):
    """ Definitions loader for json files

    Args:
        path         (str): Path to json file to be loaded
        custom      (bool): Boolean flag to specify if this is a custom provider
    """
    if not os.path.exists(path):
        return

    try:
        with open(path, encoding="utf-8") as file:
            providers = json.load(file)
        for provider in providers:
            update_definitions(provider, providers[provider], custom)
    except Exception as e:
        logging.error("Failed importing providers from %s: %s" % (path, repr(e)))


def load_overrides(path, custom=False):
    """ Overrides loader for Python files

    Note:
        Overrides must be in an ``overrides`` dictionary.

    Args:
        path    (str): Path to Python file to be loaded
        custom (bool): Boolean flag to specify if this is a custom overrides file
    """
    try:
        if custom:
            sys.path.append(path)
            from overrides import overrides
            log.debug("Imported overrides: %s", repr(overrides))
            for provider in overrides:
                update_definitions(provider, overrides[provider])
            logging.info("Successfully loaded overrides from %s", os.path.join(path, "overrides.py"))
    except Exception as e:
        import traceback
        logging.error("Failed importing %soverrides: %s", "custom " if custom else "", repr(e))


def update_definitions(provider, definition, custom=False):
    """ Updates global definitions with a single provider's definitions

    Args:
        provider     (str): Provider ID
        definition  (dict): Loaded provider's definitions to be merged with the global definitions
        custom      (bool): Boolean flag to specify if this is a custom provider
    """
    if 'base_url' in definition:
        parsed_url = urlparse(definition['base_url'])
        root_url = '%s://%s' % (parsed_url.scheme, parsed_url.netloc)
        definition['root_url'] = root_url

    if custom:
        definition['custom'] = True
        definition['enabled'] = True

    if provider in definitions:
        update(definitions[provider], definition)
    else:
        definitions[provider] = definition


def update(d, u):
    """ Utility method to recursively merge dictionary values of definitions

    Args:
        d (dict): Current provider definitions
        u (dict): Dictionary of definitions to be updated
    """
    for k, v in iteritems(u):
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


# Load providers
load_providers(os.path.join(ADDON_PATH, 'burst', 'providers', 'providers.json'))

# Load providers overrides
load_overrides(os.path.join(ADDON_PATH, 'burst', 'providers'))

# Load user's custom providers
custom_providers = os.path.join(ADDON_PATH, "providers")
if not os.path.exists(custom_providers):
    try:
        os.makedirs(custom_providers)
    except Exception as e:
        log.error("Unable to create custom providers folder: %s", repr(e))
        pass
for provider_file in glob(os.path.join(custom_providers, "*.json")):
    log.info("Importing and enabling %s" % provider_file)
    load_providers(provider_file, custom=True)

# Load user's custom overrides
custom_overrides = ADDON_PATH
if os.path.exists(os.path.join(custom_overrides, 'overrides.py')):
    load_overrides(custom_overrides, custom=True)

# Load json overrides
load_providers(os.path.join(ADDON_PATH, 'overrides.json'))

# Setting mandatory fields to their default values for each provider.
for provider in definitions:
    for k, v in iteritems(mandatory_fields):
        if k not in definitions[provider]:
            definitions[provider][k] = v

# Finding the largest provider name for further use in loggers.
longest = 10
if len(definitions) > 0:
    longest = len(definitions[sorted(definitions, key=lambda p: len(definitions[p]['name']), reverse=True)[0]]['name'])

logging.info("Loading definitions took %fs", time.time() - start_time)
