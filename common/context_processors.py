# coding: utf-8

from django.contrib.sites.models import Site

def template_context_data(request):
    variables = {
        'site': Site.objects.get_current(),
        'path': request.META['PATH_INFO'],
    }
    return variables