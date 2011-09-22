# -*- coding: utf-8 -*-

from django import template


register = template.Library()

@register.filter
def cut(value, arg):
    "Removes all values of arg from the given string"
    return value.replace(arg, '')
    
@register.filter
def replace(value, arg):
    "Replaces all arg in the given string"
    arg = arg.split()
    return value.replace(arg[0], arg[1])

@register.filter
def nowhitespace(value):
    "Removes all whitespace from the given string"
    return u"".join(value.split())

@register.filter    
def cleanwhitespace(value):
    "Removes all multiple whitespace from the given string"
    return u" ".join(value.split())
    
@register.filter
def startswith(value, arg):
    "Checks if the given string starts with arg"
    return value.startswith(arg)
    
@register.filter
def endswith(value, arg):
    "Checks if the given string ends with arg"
    return value.endswith(arg)