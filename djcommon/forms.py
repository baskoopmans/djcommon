# coding: utf-8

from django import forms
from django.forms.util import ErrorList, ErrorDict
from django.utils.translation import ugettext as _
from django.utils.functional import lazy
from django.utils.safestring import mark_safe

from .helpers import uniqify_list, camelcase_to_underscores

def add_css_classes(f, **kwargs):
    """
    Credits go to Ramen
    http://djangosnippets.org/snippets/2097/
    
    Formfield callback that adds a CSS class to every field indicating what kind of field it is.
    For example, all CharField inputs will get a class of "vCharField". If the field's widget already has a
    "class" attribute, it will be left alone.
    """

    field = f.formfield(**kwargs)
    if field and 'class' not in field.widget.attrs:
        field.widget.attrs['class'] = 'v%s' % field.__class__.__name__
        
    return field

class CombinedFieldsMixin(object):

    def __init__(self, *args, **kwargs):
        super(CombinedFieldsMixin, self).__init__(*args, **kwargs)

        if hasattr(self, 'Meta'):

            # when subclassing a subclassed form with extra fields
            # remove those fields when the field is in exclude list
            for field_name in getattr(self.Meta, 'exclude', ()):
                if field_name in self.fields:
                    del self.fields[field_name]

            # create combined_fields
            self.combined_fields = getattr(self.Meta, 'combined_fields', [])

            # for each combination create a combined field class
            for combination in self.combined_fields:
                _label_set = []
                _css_classes_set = []
                _first_field = None

                for counter, field_name in enumerate(combination):
                    field = self.fields[field_name]
                    field.combined = { 'first': False, 'last': False }

                    #_css_classes_set.append(self[field_name].css_classes())

                    if counter == 0:
                        _first_field = field
                        field.combined['first'] = True
                    elif counter == len(combination) - 1:
                        field.combined['last'] = True

                    _label_set.append(u"%s" % field.label)

                _first_field.combined['label'] = u" + ".join(uniqify_list(_label_set, preserve_order=True))
                _first_field.combined['label'] = _first_field.combined['label']
                _first_field.combined['errors'] = ErrorDict()
                _first_field.combined['css_classes'] = ' '.join(_css_classes_set)

    def _post_clean(self, *args, **kwargs):
        super(CombinedFieldsMixin, self)._post_clean(*args, **kwargs)

        if hasattr(self, 'Meta'):

            self.combined_fields = getattr(self.Meta, 'combined_fields', ())

            for combination in self.combined_fields:
                _error_set = []
                _first_field = None

                for counter, field_name in enumerate(combination):
                    field = self.fields[field_name]

                    if counter == 0:
                        _first_field = field

                    _error_set += self._errors.get(field_name, [])

                _first_field.combined['errors'] = ErrorList(uniqify_list(_error_set, True))


class EnhancedForm(CombinedFieldsMixin, forms.Form):
    error_css_class = 'error'
    required_css_class = 'required'
    formfield_callback = add_css_classes

    @property
    def name(self):
        return camelcase_to_underscores(self.__class__.__name__)


class EnhancedModelForm(CombinedFieldsMixin, forms.ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'
    formfield_callback = add_css_classes

    @property
    def name(self):
        return camelcase_to_underscores(self.__class__.__name__)


