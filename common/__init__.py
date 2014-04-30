# coding: utf-8
VERSION = (0, 3, 4)
__version__ = '.'.join(map(str, VERSION))

try:
    from django import template
    template.add_to_builtins('common.templatetags.common')
    template.add_to_builtins('common.templatetags.development')
except Exception:
    pass