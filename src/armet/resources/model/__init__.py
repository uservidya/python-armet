# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
from .base import ModelResource
from .meta import ModelResourceBase


__all__ = [
    'ModelResource'
]


class ModelResource(six.with_metaclass(ModelResourceBase, ModelResource)):
    """Implements the RESTful resource protocol for model resources.
    """