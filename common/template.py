# coding: utf-8

import os

from django.core.cache import cache
from django.template import Node


def get_available_templates(dir='', exclude=()):
    SEARCH_DIRS = []
    TEMPLATE_NAMES = []

    from django.template.loader import template_source_loaders
    try:
        for ldr in template_source_loaders:
            SEARCH_DIRS += [x for x in ldr.get_template_sources(dir)]
    except TypeError:
        pass

    for dir in SEARCH_DIRS:
        try:
            TEMPLATE_NAMES += [x for x in os.listdir(dir) if x.endswith(".html") and not x in exclude]
        except:
            pass

    return TEMPLATE_NAMES

def get_template_choices(dir='', exclude=()):
    return [(x, "%s" % (x.replace('.html', '').capitalize()),) for x in get_available_templates(dir, exclude)]


class CachedNode(Node):
    """
    Subclasses should define the methods ``get_cache_key()`` and ``get_content()`` instead of the standard render() method.
    Subclasses may also define the class attribute ``cache_timeout`` to override the default cache timeout of ten minutes.
    """

    cache_timeout = 600

    def render(self, context):
        cache_key = self.get_cache_key()
        result = cache.get(cache_key)
        if not result:
            result = self.get_content()
            cache.set(cache_key, result, self.cache_timeout)
        return result

    def get_cache_key(self):
        raise NotImplementedError

    def get_content(self):
        raise NotImplementedError


class ContextUpdatingNode(Node):
    """
    Node that updates the context with certain values.
    Subclasses should define ``get_extra_context()``, which should return a dictionary to be added to the context.
    """

    def render(self, context):
        context.update(self.get_extra_context())
        return ''

    def get_extra_context(self):
        raise NotImplementedError


class CachedContextUpdatingNode(CachedNode, ContextUpdatingNode):

    def get_content(self):
        return self.get_extra_context()

    def render(self, context):
        context.update(CachedNode.render(self, context))
        return ''