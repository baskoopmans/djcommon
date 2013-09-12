# coding: utf-8

import sys
import re

from importlib import import_module
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import simplejson


# for formatting Decimal objects
TWOPLACES = Decimal(10) ** -2


def camelcase_to_underscores(string):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', str(string))
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def get_setting(name, default=None):
    return getattr(settings, name, default)

def uniqify_list(list, preserve_order=False):
    if preserve_order:
        # Order preserving
        seen = set()
        return [x for x in list if x not in seen and not seen.add(x)]
    else:
        # Not order preserving, faster than the function above.
        return {}.fromkeys(list).keys()

def contains(list, filter):
    """
    Example: if contains(a_list, lambda x: x.n == 3)  # True if any element has .n==3
    """
    for x in list:
        if filter(x):
            return True
    return False

def get_json_object(request):
    data = None
    if request.body:
        try:
            data = simplejson.loads(request.body.replace("'","\""), encoding='utf-8')
        except:
            data = data

    if data and type(data) is dict:
        return data

def model_field_has_changed(instance, field):
    """
    Check if a given field on a model has changed
    """
    if not instance.pk:
        return False
    try:
        old_value = instance.__class__._default_manager.filter(pk=instance.pk).values(field).get()[field]
    except ObjectDoesNotExist:
        return False
    return not getattr(instance, field) == old_value

def touch(path):
    import os, time
    now = time.time()
    try:
        os.utime(path, (now, now))
    except os.error:
        raise Exception("Touching '%s' failed" % path)

def construct_object(location, **kwargs):
    module, object = location.rsplit(".", 1)
    return getattr(import_module(module), object)(**kwargs)

def reload_urlconf():
    if settings.ROOT_URLCONF in sys.modules:
        reload(sys.modules[settings.ROOT_URLCONF])
    return import_module(settings.ROOT_URLCONF)