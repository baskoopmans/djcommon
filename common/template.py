# coding: utf-8

import os

from django.template.loader_tags import BlockNode, ExtendsNode
from django.template import loader, Context, RequestContext, TextNode

from helpers import uniqify_list


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
