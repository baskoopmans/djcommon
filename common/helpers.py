# -*- coding: utf-8 -*-

from decimal import Decimal 

from django.conf import settings


# for formatting Decimal objects
TWOPLACES = Decimal(10) ** -2

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