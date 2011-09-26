# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms

from common.widgets.admin import VerboseManyToManyRawIdWidget


class EnhancedModelAdmin(admin.ModelAdmin):

    def formfield_for_manytomany(self, db_field, **kwargs):
        """
        Check `raw_id_fields` for `db_field_name` and use VerboseManyToManyRawIdWidget for m2m relationships
        """
        if db_field.name in self.raw_id_fields:
            kwargs.pop('request', None)
            kwargs['widget'] = VerboseManyToManyRawIdWidget(db_field.rel)
            return db_field.formfield(**kwargs)
        
        return super(EnhancedModelAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
        

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
        result = super(EnhancedModelAdmin, self).change_view(request, object_id, extra_context )
        
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

class EnhancedModelAdmin(admin.options.InlineModelAdmin):
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name in self.raw_id_fields:
            kwargs['widget'] = VerboseManyToManyRawIdWidget(db_field.rel)
            return db_field.formfield(**kwargs)
        return super(EnhancedModelAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class EnhancedStackedInline(admin.StackedInline, EnhancedModelAdmin):
    pass


class EnhancedTabularInline(admin.TabularInline, EnhancedModelAdmin):
    pass
