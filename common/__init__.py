VERSION = (0, 1, 0)
__version__ = '.'.join(map(str, VERSION))

from django import template
template.add_to_builtins('common.templatetags.common')
template.add_to_builtins('common.templatetags.development')

# Add db_name to options for use in model.Meta class
import django.db.models.options as options
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('db_name',)