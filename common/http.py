# coding: utf-8

from django.http import HttpResponse
from django.utils import simplejson


class JsonResponse(HttpResponse):
    """
    JSON response
    """
    def __init__(self, content, mimetype='application/json', status=None, content_type=None):
        super(JsonResponse, self).__init__(
            content=simplejson.dumps(content, indent=4, encoding='utf-8', sort_keys=True),
            mimetype=mimetype,
            status=status,
            content_type=content_type,
        )