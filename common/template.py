# coding: utf-8

import os

from django.template import loader

from helpers import uniqify_list

def get_available_templates(dir=''):
    SEARCH_DIRS = []
    TEMPLATE_NAMES = []

    for ldr in loader.template_source_loaders:
        SEARCH_DIRS += [x for x in ldr.get_template_sources(dir)]

    for dir in SEARCH_DIRS:
        try:
            TEMPLATE_NAMES += [x for x in os.listdir(dir) if x.endswith(".html")]
        except:
            pass

    return uniqify_list(TEMPLATE_NAMES)

def get_template_choices(dir=''):
    return [(x, "%s (%s)" % (x.replace('.html', '').capitalize(), x)) for x in get_available_templates(dir)]
