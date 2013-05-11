# coding: utf-8

from django.http import HttpResponseNotAllowed
from django.shortcuts import render_to_response
from django.template import RequestContext


def server_error(request, template_name='500.html'):
    """
    Custom 500 error handler for adding context to the template.
    """
    return render_to_response(template_name, context_instance=RequestContext(request))

class RESTmethod(object):
    methods = ['GET','POST','PUT','DELETE']

    def __call__(self, request, *args, **kwargs):
        callback = getattr(self, request.method.lower(), None)
        if callback:
            return callback(request, *args, **kwargs)
        else:
            return HttpResponseNotAllowed(self.get_allowed_methods())

    def get_allowed_methods(self):
        return [method for method in self.methods if hasattr(self, method.lower())]
