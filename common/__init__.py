VERSION = (0, 1, 0)
__version__ = '.'.join(map(str, VERSION))

try:
    from django import template
    template.add_to_builtins('common.templatetags.common')
    template.add_to_builtins('common.templatetags.development')
except:
    pass