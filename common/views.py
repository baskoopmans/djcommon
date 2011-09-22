# Copyright 2011 - The New Style, all rights reserved.
# It is forbidden to alter, duplicate or redistribute any part of this document.
# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext


def server_error(request, template_name='500.html'):
    """
    Custom 500 error handler for adding context to the template.
    """
    return render_to_response(template_name, context_instance=RequestContext(request))