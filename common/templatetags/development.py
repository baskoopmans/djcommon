# coding: utf-8

from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def attributes(value):
    """
    Returns a list with attributes for the object
    Example: {{ variable|attributes }}
    """
    return [attribute for attribute in dir(value) if not attribute.startswith('_')]
    
@register.filter
def attributes_formatted(value):
    """
    Returns a list with attributes for the object
    Example: {{ variable|attributes_formatted }}
    """
    attribute_list = attributes(value)
    output = '<pre>'
    for attribute in attribute_list:
        try:
            attribute_content = "%s (%s)" % (getattr(value, attribute), attributes(getattr(value, attribute)))
        except:
            attribute_content = ''
        output += '\t%s: %s\n' % (attribute, attribute_content)
    output += '</pre>'
    return mark_safe(output)
 
@register.filter
def getattribute(value, arg):
    """
    Gets an attribute of an object dynamically from a string name
    Example: {{ variable|getattribute:"name" }}
    Example: {{ variable|getattribute:variable }}
    """

    if hasattr(value, str(arg)):
        return getattr(value, arg)
    elif hasattr(value, 'has_key'):
        if value.has_key(arg):
            return value[arg]
        else:
            return ''
    elif value.isdigit():
        return value[int(arg)]
    else:
        return ''