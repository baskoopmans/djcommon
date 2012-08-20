# coding: utf-8

from django import forms
from django.forms.util import ErrorList, ErrorDict
from django.utils.copycompat import deepcopy
from django.utils.translation import ugettext as _
from django.utils.functional import lazy

from helpers import uniqify_list

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


class EnhancedForm(forms.Form):
    error_css_class = 'error'
    required_css_class = 'required'
    formfield_callback = add_css_classes
    
                    
class EnhancedModelForm(forms.ModelForm):
    error_css_class = EnhancedForm.error_css_class
    required_css_class = EnhancedForm.required_css_class
    formfield_callback = EnhancedForm.formfield_callback

    def __init__(self, *args, **kwargs):
        super(EnhancedModelForm, self).__init__(*args, **kwargs)

        # when subclassing a subclassed form with extra fields
        # remove those fields when the field is in exclude list
        for field_name in getattr(self.Meta, 'exclude', ()):
            if self.fields.has_key(field_name):
                del self.fields[field_name]

        # create combined_fields
        self.combined_fields = getattr(self.Meta, 'combined_fields', ())

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

                _label_set.append(field.label.lower())

            _first_field.combined['label'] = ' + '.join(_label_set)
            _first_field.combined['label'] = _first_field.combined['label'].capitalize()
            _first_field.combined['css_classes'] = ' '.join(_css_classes_set)

    def _post_clean(self, *args, **kwargs):
        super(EnhancedModelForm, self)._post_clean(*args, **kwargs)

        self.combined_fields = getattr(self.Meta, 'combined_fields', ())

        for combination in self.combined_fields:
            _error_set = []
            _first_field = None

            for counter, field_name in enumerate(combination):
                field = self.fields[field_name]

                if counter == 0:
                    _first_field = field

                _error_set += self.errors.get(field_name, [])

            _first_field.combined['errors'] = ErrorList(uniqify_list(_error_set, True))
