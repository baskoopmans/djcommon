# encoding: utf-8

from django import conf
from django.db.models.loading import cache


def site(request):
    """
    A context processor to add the "site" object to the current Context.
    To add the 'current_site' context processor to your project, add the
    'djcommon.context_processors.current_site' module in the
    TEMPLATE_CONTEXT_PROCESSORS setting in your settings.py file
    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        'djcommon.context_processors.site',
        ...
    )
    """
    try:
        site = cache.get_model('sites', 'Site')
        return dict(site=site.objects.get_current)
    except Site.DoesNotExist:
        return dict(site=None)

def path(request):
    """
    A context processor to add the "path" to the current Context.
    To add the 'path' context processor to your project, add the
    'djcommon.context_processors.path' module in the
    TEMPLATE_CONTEXT_PROCESSORS setting in your settings.py file
    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        'djcommon.context_processors.path',
        ...
    )
    """
    return dict(path=request.META['PATH_INFO'])

def settings(request):
    """
    A context processor to add the "settings" object to the current Context.
    To add the 'settings' context processor to your project, add the
    'djcommon.context_processors.settings' module in the
    TEMPLATE_CONTEXT_PROCESSORS setting in your settings.py file
    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        'djcommon.context_processors.settings',
        ...
    )
    """
    return dict(settings=conf.settings)
