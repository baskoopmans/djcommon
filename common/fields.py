# -*- coding: utf-8 -*-

from django import forms
from django.db import models
from django.db.models.fields import CharField
from django.utils.encoding import force_unicode, StrAndUnicode
from django.utils.text import capfirst

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


class Country(StrAndUnicode):
    def __init__(self, code):
        self.code = code
    
    def __unicode__(self):
        return force_unicode(self.code or u'')

    def __eq__(self, other):
        return unicode(self) == force_unicode(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __cmp__(self, other):
        return cmp(unicode(self), force_unicode(other))

    def __hash__(self):
        return hash(unicode(self))

    def __repr__(self):
        return "%s(code=%r)" % (self.__class__.__name__, unicode(self))

    def __nonzero__(self):
        return bool(self.code)

    def __len__(self):
        return len(unicode(self))
    
    @property
    def name(self):
        # Local import so the countries aren't loaded unless they are needed. 
        from common.conf.countries import COUNTRIES
        for code, name in COUNTRIES:
            if self.code == code:
                return name
        return ''

    
class CountryDescriptor(object):
    """
    A descriptor for country fields on a model instance. Returns a Country when
    accessed so you can do stuff like::

        >>> instance.country.name
        u'New Zealand'

        >>> instance.country.flag
        '/static/flags/nz.gif'
    """
    def __init__(self, field):
        self.field = field

    def __get__(self, instance=None, owner=None):
        if instance is None:
            raise AttributeError(
                "The '%s' attribute can only be accessed from %s instances."
                % (self.field.name, owner.__name__))
        return Country(code=instance.__dict__[self.field.name])

    def __set__(self, instance, value):
        if value is not None:
            value = force_unicode(value)
        instance.__dict__[self.field.name] = value


class CountryField(CharField):
    """
    A country field for Django models that provides all ISO 3166-1 countries as choices.
    """
    descriptor_class = CountryDescriptor
 
    def __init__(self, *args, **kwargs):
        # Local import so the countries aren't loaded unless they are needed. 
        from common.conf.countries import COUNTRIES

        kwargs.setdefault('max_length', 2) 
        kwargs.setdefault('choices', COUNTRIES) 

        super(CharField, self).__init__(*args, **kwargs) 

    def get_internal_type(self): 
        return "CharField"

    def contribute_to_class(self, cls, name):
        super(CountryField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, self.descriptor_class(self))

    def get_prep_lookup(self, lookup_type, value):
        if hasattr(value, 'code'):
            value = value.code
        return super(CountryField, self).get_prep_lookup(lookup_type, value)

    def pre_save(self, *args, **kwargs):
        "Returns field's value just before saving."
        value = super(CharField, self).pre_save(*args, **kwargs)
        return self.get_prep_value(value)

    def get_prep_value(self, value):
        "Returns field's value prepared for saving into a database."
        # Convert the Country to unicode for database insertion.
        if value is None:
            return None
        return unicode(value)


# If south is installed, ensure that CountryField and MultiSelectField will be introspected just like a normal CharField.
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ['^common\.fields\.CountryField'])
    add_introspection_rules([], ['^common\.fields\.MultiSelectField'])
except ImportError:
    pass
