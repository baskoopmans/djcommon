# coding: utf-8

import os
import traceback

from django.utils.safestring import SafeString


def cached(function):
    """
    Save the result of this <function> in object.<function>_cache attribute
    """
    def _get_from_objects_cache(object, *args, **kwargs):
        if type(function) is property:
            raise Exception('%s is a property of %s' % (function, object))
        else:
            function_name = function.__name__
            cache_key = '%s_cache' % function_name
            
        if getattr(object, cache_key, False):
            result = getattr(object, cache_key)
        else:
            result = function(object)
            setattr(object, cache_key, result)
        
        return result
            
    return _get_from_objects_cache