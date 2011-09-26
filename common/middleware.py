# -*- coding: utf-8 -*-

import re

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden, get_host


class StripWhitespaceMiddleware:
    """
    Strips leading and trailing whitespace from response content.
    """
    RE_WHITESPACE = re.compile('\s*\n')
    
    def process_response(self, request, response):
        if 'text/html' in response['Content-Type']:
            response.content = self.RE_WHITESPACE.sub('\n', response.content)
            if response.content[:1] == '\n':
                response.content = response.content[1:]
                
        return response


class RestrictedAccessMiddleware(object):
    """
    This middleware restrict access to site for not authenticated users.
    or allows users with a given ip address
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        
        RESTRICTED_ACCESS_ALLOWED_IPS = getattr(settings, 'RESTRICTED_ACCESS_ALLOWED_IPS', ())
        REMOTE_ADDR = request.META.get('HTTP_X_REAL_IP', request.META.get('REMOTE_ADDR', None))
        
        if REMOTE_ADDR in RESTRICTED_ACCESS_ALLOWED_IPS:
            return None
            
        RESTRICTED_ACCESS_LEVEL = getattr(settings, 'RESTRICTED_ACCESS_LEVEL', None) # authenticated, staff, super admins
        if RESTRICTED_ACCESS_LEVEL in ('authenticated', 'staff', 'superusers') and \
            not request.path.startswith(('settings.LOGIN_URL', reverse('admin:index'),)):
            if not hasattr(request, 'user'):
                raise ImproperlyConfigured(
                    "RestrictedAccessMiddleware requires the authentication middleware to be installed. "
                    "Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                    " before the RestrictStaffToAdminMiddleware class.")
            elif request.user.is_authenticated():
                if (RESTRICTED_ACCESS_LEVEL == 'staff' and not request.user.is_staff) or \
                    (RESTRICTED_ACCESS_LEVEL == 'superusers' and not request.user.is_superusers):
                    return HttpResponseForbidden('You\'re access is restricted. <a href="%s">Logout</a>' % reverse('admin:logout'))
            else:
                return HttpResponseRedirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        else:
            return None


class SSLMiddleware:
    """
    Based on https://github.com/rossdakin/django-heroism/blob/master/heroism/middleware.py
    If a specific header is present in the request, we redefine the request
    object's is_secure method to reflect whether or not the header's value
    is the specified secure protocol (e.g. "https"), defaulting to insecure.
    """

    def process_request(self, request):
        if 'HTTP_X_FORWARDED_SECURE' and 'HTTP_X_FORWARDED_SCHEME' in request.META:
            if request.META['HTTP_X_FORWARDED_SECURE'] == getattr(settings, 'SECURE_REQUEST_HEADER_SECRET_KEY', 'https') \
                and request.META['HTTP_X_FORWARDED_SCHEME'] == 'https':
                request.is_secure = lambda: True
            else:
                request.is_secure = lambda: False

    def process_view(self, request, view_func, view_args, view_kwargs):
            if 'SSL' in view_kwargs:
                if getattr(settings, 'SSL_MIDDLEWARE_SECURED', True):
                    secure = view_kwargs['SSL']
                else:
                    secure = False
                del view_kwargs['SSL']
            else:
                secure = False
            
            if not secure == request.is_secure():
                return self._redirect(request, secure)
                        
    def _redirect(self, request, secure):
        protocol = secure and "https" or "http"
        newurl = "%s://%s%s" % (protocol, get_host(request), request.get_full_path())

        if settings.DEBUG and request.method == 'POST':
            raise RuntimeError, \
            """Django can't perform a SSL redirect while maintaining POST data.
            Please structure your views so that redirects only occur during GETs."""

        return HttpResponseRedirect(newurl)