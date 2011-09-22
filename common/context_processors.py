# Copyright 2011 - The New Style, all rights reserved.
# It is forbidden to alter, duplicate or redistribute any part of this document.
# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.sites.models import Site


def template_context_data(request):
    variables = {
        'site': Site.objects.get_current(),
        'path': request.META['PATH_INFO'],
        'settings': settings,
        'DEFAULT_MEDIA_URL': settings.DEFAULT_MEDIA_URL,
        'SITE_NAME': settings.SITE_NAME,
        'SITE_SLOGAN': settings.SITE_SLOGAN,
        'SITE_MEDIA_URL': settings.SITE_MEDIA_URL,
        'PHONE_NUMBER': settings.PHONE_NUMBER,
        'THEME_MEDIA_URL': settings.THEME_MEDIA_URL,
        'THEME_NAME': settings.THEME_NAME,
        'GOOGLE_ANALYTICS_UA': settings.GOOGLE_ANALYTICS_UA,
    }
    return variables