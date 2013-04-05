# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
import re
import collections
import os
import pkgutil
import importlib
import functools


def cons(collection, value):
    """Extends a collection with a value."""
    if isinstance(value, collections.Mapping):
        if collection is None:
            collection = {}
        collection.update(**value)

    elif isinstance(value, six.string_types):
        if collection is None:
            collection = []
        collection.append(value)

    elif isinstance(value, collections.Iterable):
        if collection is None:
            collection = []
        collection.extend(value)

    else:
        if collection is None:
            collection = []
        collection.append(value)

    return collection
