# coding: utf-8

import os
import traceback

from django.utils.safestring import SafeString
from django.utils.decorators import method_decorator


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


def class_decorator(decorator):
    """
    usage:
    in views.py

        from django.views.decorators.cache import cache_control
        from django.views.generic import View
        @class_decorator(cache_control(max_age=60))
        class MyView(View):
            filename = 'templatefile'
            def content(self, request):
                ...
    """
    def inner(cls):
        orig_dispatch = cls.dispatch
        @method_decorator(decorator)
        def new_dispatch(self, request, *args, **kwargs):
            return orig_dispatch(self, request, *args, **kwargs)
        cls.dispatch = new_dispatch
        return cls
    return inner