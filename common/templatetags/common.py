# -*- coding: utf-8 -*-

import re

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter_function
def random_slice(value, arg=1):
    """
    Returns one or more random item(s) from the list
    """
    try:
        arg = int(arg)
    except ValueError:
        return value
    if arg == 1:
        return random.sample(value, arg)
    elif len(value) > arg:  # Only pick if we are asked for fewer items than we are given
        return random.sample(value, arg)
    else:   # Number requested is equal to or greater than the number we have, return them all in random order
        new_list = list(value)
        random.shuffle(new_list)
        return new_list

@register.filter
@stringfilter
def cleartags(value, tags):
    tags = [re.escape(tag) for tag in tags.split()]
    tags_re = u'(%s)' % u'|'.join(tags)
    clear_re = re.compile("<\s*%s[^>]*>(.*?)<\s*/\s*\\1>" % tags_re, re.U)
    value = clear_re.sub('', value)
    return value
cleartags.is_safe = True

@register.filter
@stringfilter
def cut(value, arg):
    "Removes all values of arg from the given string"
    return value.replace(arg, '')
cut.is_safe = True

@register.filter
@stringfilter
def replace(value, arg):
    "Replaces all arg in the given string"
    arg = arg.split()
    return value.replace(arg[0], arg[1])
replace.is_safe = True

@register.filter
def nowhitespace(value):
    "Removes all whitespace from the given string"
    return u"".join(value.split())
nowhitespace.is_safe = True

@register.filter    
def cleanwhitespace(value):
    "Removes all multiple whitespace from the given string"
    return u" ".join(value.split())
cleanwhitespace.is_safe = True

@register.filter
@stringfilter
def startswith(value, arg):
    "Checks if the given string starts with arg"
    return value.startswith(arg)
    
@register.filter
@stringfilter
def endswith(value, arg):
    "Checks if the given string ends with arg"
    return value.endswith(arg)