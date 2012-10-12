# coding: utf-8

from decimal import Decimal 

from django.conf import settings
from django.utils import simplejson


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
    old_value = instance.__class__._default_manager.filter(pk=instance.pk).values(field).get()[field]
    return not getattr(instance, field) == old_value