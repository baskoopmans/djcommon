# encoding: utf-8

import hashlib

from django import forms
from django.db import models
from django.db.models.fields import CharField
from django.utils.text import capfirst


class HashField(models.CharField):
    description = ('HashField is related to some other field in a model and'
        'stores its hashed value for better indexing performance.')

    def __init__(self, field_names='', *args, **kwargs):
        """
        :param field_names: name of the field or fields storing the value to be hashed
        """
        self.field_names = field_names
        kwargs['max_length'] = 40
        kwargs['null'] = False
        kwargs.setdefault('db_index', True)
        kwargs.setdefault('editable', False)
        super(HashField, self).__init__(*args, **kwargs)

    def calculate_hash(self, model_instance):
        string_to_hash = ''
        for field_name in self.field_names.split(','):
            field_name = field_name.strip()
            field_value = getattr(model_instance, field_name)
            field_value = u"{0}".format(field_value)
            string_to_hash += hashlib.sha1(field_value.encode('utf-8')).hexdigest()

        hash = hashlib.sha1(string_to_hash).hexdigest()
        setattr(model_instance, self.attname, hash)
        return hash

    def pre_save(self, model_instance, add):
        self.calculate_hash(model_instance)
        return super(HashField, self).pre_save(model_instance, add)


class LazyChoiceField(forms.ChoiceField):
    #def __init__(self, choices=(), required=True, widget=None, label=None, initial=None, help_text=None, *args, **kwargs):
    #    super(LazyChoiceField, self).__init__(choices=choices, required=required, widget=widget, label=label, initial=initial, help_text=help_text, *args, **kwargs)

    def valid_value(self, value):
        return True


class MultiSelectFormField(forms.MultipleChoiceField):
    widget = forms.CheckboxSelectMultiple

    def __init__(self, *args, **kwargs):
        self.max_choices = kwargs.pop('max_choices', 0)
        super(MultiSelectFormField, self).__init__(*args, **kwargs)
        self.initial = kwargs.pop('initial', '').split(',')

    def clean(self, value):
        if not value and self.required:
            raise forms.ValidationError(self.error_messages['required'])
        if value and self.max_choices and len(value) > self.max_choices:
            raise forms.ValidationError('You must select a maximum of %s choice%s.'
                    % (apnumber(self.max_choices), pluralize(self.max_choices)))
        return value


class MultiSelectField(models.Field):
    """
    Credits go to Daniel Roseman
    http://djangosnippets.org/snippets/1200/
    """
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return "CharField"

    def get_choices_default(self):
        return self.get_choices(include_blank=False)

    def _get_FIELD_display(self, field):
        value = getattr(self, field.attname)
        choicedict = dict(field.choices)

    def formfield(self, **kwargs):
        # don't call super, as that overrides default widget if it has choices
        defaults = {'required': not self.blank, 'label': capfirst(self.verbose_name),
                    'help_text': self.help_text, 'choices':self.choices}
        if self.has_default():
            defaults['initial'] = self.get_default()
        defaults.update(kwargs)
        return MultiSelectFormField(**defaults)

    def get_db_prep_value(self, value, connection=None, prepared=False):
        if isinstance(value, basestring):
            return value
        elif isinstance(value, list):
            return ",".join(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

    def to_python(self, value):
        if isinstance(value, list):
            return value
        elif value==None:
            return ''
        return value.split(",")

    def validate(self, value, model_instance):
        return

    def contribute_to_class(self, cls, name):
        super(MultiSelectField, self).contribute_to_class(cls, name)
        if self.choices:
            func = lambda self, fieldname = name, choice = None, choicedict = dict(self.choices): "%s" % choicedict.get(choice) if choice else ", ".join([choicedict.get(value,value) for value in getattr(self,fieldname)])
            setattr(cls, 'get_%s_display' % self.name, func)


class IntegerRangeField(models.IntegerField):

    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.IntegerField.__init__(self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value':self.max_value}
        defaults.update(kwargs)
        return super(IntegerRangeField, self).formfield(**defaults)


class SmallIntegerRangeField(models.SmallIntegerField):

    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.SmallIntegerField.__init__(self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value':self.max_value}
        defaults.update(kwargs)
        return super(SmallIntegerRangeField, self).formfield(**defaults)


# Add introspection rules for fields for South
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ['^djcommon\.fields\.HashField'])
    add_introspection_rules([], ['^djcommon\.fields\.MultiSelectField'])
    add_introspection_rules([], ['^djcommon\.fields\.IntegerRangeField'])
    add_introspection_rules([], ['^djcommon\.fields\.SmallIntegerRangeField'])
except ImportError:
    pass
