# coding: utf-8

import os
import traceback

from django.utils.safestring import SafeString


def print_debug(function):
    """
    Reterns exception's debug when in <function> an error is raised.
    """
    def _print_debug(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception, e:
            debug_info = []
            for i, item in enumerate(traceback.extract_stack()[:]):
                debug_info.append(", ".join([type(e).__name__, e.message, os.path.basename(item[0]), str(item[1])]))
            result = "\r\n".join(debug_info)
            return SafeString("<pre>%s</pre>" % result)
            
    return _print_debug

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