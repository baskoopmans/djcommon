# coding: utf-8

from django.contrib import admin
from django.contrib.contenttypes.generic import GenericForeignKey
from django.db import transaction
from django.db.models import get_models, Model
from django import forms

from .widgets.admin import VerboseManyToManyRawIdWidget


@transaction.commit_on_success
def merge_model_objects(primary_object, alias_objects=[], keep_old=False):
    """
    Use this function to merge model objects (i.e. Users, Organizations, Polls,
    etc.) and migrate all of the related fields from the alias objects to the
    primary object.

    Usage:
    from django.contrib.auth.models import User
    primary_user = User.objects.get(email='good_email@example.com')
    duplicate_user = User.objects.get(email='good_email+duplicate@example.com')
    merge_model_objects(primary_user, duplicate_user)
    """
    if not isinstance(alias_objects, list):
        alias_objects = [alias_objects]

    # check that all aliases are the same class as primary one and that
    # they are subclass of model
    primary_class = primary_object.__class__

    if not issubclass(primary_class, Model):
        raise TypeError('Only django.db.models.Model subclasses can be merged')

    for alias_object in alias_objects:
        if not isinstance(alias_object, primary_class):
            raise TypeError('Only models of same class can be merged')

    # Get a list of all GenericForeignKeys in all models
    # TODO: this is a bit of a hack, since the generics framework should provide a similar
    # method to the ForeignKey field for accessing the generic related fields.
    generic_fields = []
    for model in get_models():
        for field_name, field in filter(lambda x: isinstance(x[1], GenericForeignKey), model.__dict__.iteritems()):
            generic_fields.append(field)

    blank_local_fields = set([field.attname for field in primary_object._meta.local_fields if getattr(primary_object, field.attname) in [None, '']])

    # Loop through all alias objects and migrate their data to the primary object.
    for alias_object in alias_objects:
        # Migrate all foreign key references from alias object to primary object.
        for related_object in alias_object._meta.get_all_related_objects():
            # The variable name on the alias_object model.
            alias_varname = related_object.get_accessor_name()
            # The variable name on the related model.
            obj_varname = related_object.field.name
            related_objects = getattr(alias_object, alias_varname)
            # Check if the related_objects is a related manager or an object
            if hasattr(related_objects, 'all'):
                for obj in related_objects.all():
                    setattr(obj, obj_varname, primary_object)
                    obj.save()
            else:
                setattr(related_objects, obj_varname, primary_object)
                related_objects.save()

        # Migrate all many to many references from alias object to primary object.
        for related_many_object in alias_object._meta.get_all_related_many_to_many_objects():
            alias_varname = related_many_object.get_accessor_name()
            obj_varname = related_many_object.field.name

            if alias_varname is not None:
                # standard case
                related_many_objects = getattr(alias_object, alias_varname).all()
            else:
                # special case, symmetrical relation, no reverse accessor
                related_many_objects = getattr(alias_object, obj_varname).all()
            for obj in related_many_objects.all():
                getattr(obj, obj_varname).remove(alias_object)
                getattr(obj, obj_varname).add(primary_object)

        # Migrate all generic foreign key references from alias object to primary object.
        for field in generic_fields:
            filter_kwargs = {}
            filter_kwargs[field.fk_field] = alias_object._get_pk_val()
            filter_kwargs[field.ct_field] = field.get_content_type(alias_object)
            for generic_related_object in field.model.objects.filter(**filter_kwargs):
                setattr(generic_related_object, field.name, primary_object)
                generic_related_object.save()

        # Try to fill all missing values in primary object by values of duplicates
        filled_up = set()
        for field_name in blank_local_fields:
            val = getattr(alias_object, field_name)
            if val not in [None, '']:
                setattr(primary_object, field_name, val)
                filled_up.add(field_name)
        blank_local_fields -= filled_up

        if not keep_old:
            alias_object.delete()
    primary_object.save()
    return primary_object


def merge_selected_objects(self, request, queryset):
    main = queryset[0]
    tail = [x for x in queryset[1:]]

    related = main._meta.get_all_related_objects()

    merge_model_objects(main, tail)

    self.message_user(request, "%s is merged with %s." % (main, tail))
merge_selected_objects.short_description = "Merge selected objects"

admin.site.add_action(merge_selected_objects, 'merge_selected_objects')


class EnhancedModelAdmin(admin.ModelAdmin):

    def get_fieldsets(self, request, obj=None):
        """
        Check `add_fieldsets` and only display those when action is add
        """
        if not obj and hasattr(self, 'add_fieldsets'):
            return self.add_fieldsets
        return super(EnhancedModelAdmin, self).get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form when add_form is supplied
	    """
        defaults = {}
        if obj is None and hasattr(self, 'add_form'):
            defaults.update({
                'form': self.add_form,
                'fields': admin.util.flatten_fieldsets(self.add_fieldsets),
            })
        defaults.update(kwargs)
        return super(EnhancedModelAdmin, self).get_form(request, obj, **defaults)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Check `raw_id_fields` for `db_field_name` and use VerboseManyToManyRawIdWidget for m2m relationships
        """
        if db_field.name in self.raw_id_fields:
            kwargs.pop('request', None)
            kwargs['widget'] = VerboseManyToManyRawIdWidget(db_field.rel)
            return db_field.formfield(**kwargs)
        
        return super(EnhancedModelAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def response_add(self, request, obj, post_url_continue='../%s/'):
        """
        Determines the HttpResponse for the add_view stage. It mostly defers to
        its superclass implementation but is customized because the Admins with a
        has a slightly different workflow.
        """
        # We should allow further modification of the user just added i.e. the
        # 'Save' button should behave like the 'Save and continue editing'
        # button except in two scenarios:
        # * The user has pressed the 'Save and add another' button
        # * We are adding a user in a popup
        if hasattr(self, 'add_fieldsets') and '_addanother' not in request.POST and '_popup' not in request.POST:
            request.POST['_continue'] = 1
        return super(EnhancedModelAdmin, self).response_add(request, obj, post_url_continue)

    def add_view(self, request, *args, **kwargs):
        """
        Delete the session key, since we want the user to be directed to all listings
        after a save on a new object.
        """
        result = super(EnhancedModelAdmin, self).add_view(request, *args, **kwargs )
        request.session['filtered'] =  None

        return result
            
    def change_view(self, request, object_id, extra_context={}):
        """
        Used to redirect users back to their filtered list of locations if there were any.
        Save the referer of the page to return to the filtered change_list after saving the page
        """
        result = super(EnhancedModelAdmin, self).change_view(request, object_id, extra_context=extra_context)
        #raise Exception(result)
        
        # Look at the referer for a query string '^.*\?.*$'
        ref = request.META.get('HTTP_REFERER', '')
        if ref.find('?') != -1:
            # We've got a query string, set the session value
            request.session['filtered'] =  ref
        
        if request.POST.has_key('_save'):
            try:
                if request.session['filtered'] is not None:
                    result['Location'] = request.session['filtered']
                    request.session['filtered'] = None
            except Exception:
                pass
                
        return result

class EnhancedInlineModelAdmin(admin.options.InlineModelAdmin):
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name in self.raw_id_fields:
            kwargs['widget'] = VerboseManyToManyRawIdWidget(db_field.rel)
            return db_field.formfield(**kwargs)
        return super(EnhancedInlineModelAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class EnhancedStackedInline(admin.StackedInline, EnhancedInlineModelAdmin):
    pass


class EnhancedTabularInline(admin.TabularInline, EnhancedInlineModelAdmin):
    pass
