VERSION = (0, 0, 0)
__version__ = '.'.join(map(str, VERSION))


from django import template
template.add_to_builtins('common.templatetags.common')
template.add_to_builtins('common.templatetags.development')