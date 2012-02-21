# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms

from common.widgets.admin import VerboseManyToManyRawIdWidget


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
