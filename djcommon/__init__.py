# coding: utf-8
VERSION = (1, 1, 1)
__version__ = '.'.join(map(str, VERSION))

try:
    from django import template
    template.add_to_builtins('djcommon.templatetags.common')
    template.add_to_builtins('djcommon.templatetags.development')
except Exception:
    pass
