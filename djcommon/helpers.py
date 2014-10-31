# coding: utf-8

import sys
import re
import copy
import json
import random

from importlib import import_module
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


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

def random_slice_list(value, arg):
    # Only pick if we are asked for fewer items than we are given
    # Else number requested is equal to or greater than the number we have, return them all in random order
    if len(value) > arg or arg == 1:
        value = random.sample(value, arg)
    else:
        random.shuffle(value)

    return value

def list_contains(list, filter):
    """Example: if list_contains(a_list, lambda x: x.n == 3)  # True if any element has .n==3"""
    for x in list:
        if filter(x):
            return True
    return False

def hash_recursive(mutable):
  if isinstance(mutable, (set, tuple, list)):
    return tuple([hash_recursive(item) for item in mutable])
  elif not isinstance(mutable, dict):
    return hash(mutable)

  new_mutable = copy.deepcopy(mutable)
  for key, value in new_mutable.items():
    new_mutable[key] = hash_recursive(value)

  return hash(tuple(frozenset(sorted(new_mutable.items()))))

def get_json_object(request):
    data = None
    if request.body:
        try:
            data = json.loads(request.body.replace("'","\""), encoding='utf-8')
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
