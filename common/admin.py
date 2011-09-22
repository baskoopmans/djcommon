# Copyright 2011 - The New Style, all rights reserved.
# It is forbidden to alter, duplicate or redistribute any part of this document.
# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms

from novomore.apps.common.widgets.admin import VerboseManyToManyRawIdWidget
from novomore.apps.catalog.models import Product, Option, AdditionalOption
from novomore.apps.pricing.models import Offer


class EnhancedModelAdminForm(forms.ModelForm):
    pass

class EnhancedModelAdmin(admin.ModelAdmin):

#    def get_form(self, request, obj=None, **kwargs):
#        # save obj reference for future processing in Inline
#        request._obj_ = obj
#        return super(EnhancedModelAdmin, self).get_form(request, obj, **kwargs)
        
    def formfield_for_manytomany(self, db_field, **kwargs):
        if db_field.name in self.raw_id_fields:
            kwargs.pop('request', None)
            kwargs['widget'] = VerboseManyToManyRawIdWidget(db_field.rel)
            return db_field.formfield(**kwargs)
        return super(EnhancedModelAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
        

    def add_view(self, request, *args, **kwargs):
            result = super(EnhancedModelAdmin, self).add_view(request, *args, **kwargs )
            """
            Delete the session key, since we want the user to be directed to all listings
            after a save on a new object.
            """
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
            """
            We only kick into action if we've saved and if
            there is a session key of 'filtered', then we
            delete the key.
            """
            try:
                if request.session['filtered'] is not None:
                    result['Location'] = request.session['filtered']
                    request.session['filtered'] = None
            except:
                pass
                
        return result

        
class EnhancedInlineFormSet(forms.models.BaseInlineFormSet):
    def add_fields(self, form, index):
        super(EnhancedInlineFormSet, self).add_fields(form, index)
        
        options = Option.objects.none()
        if form.instance:
            try:    
                try:
                    product = form.instance.product    
                except AttributeError:
                    product = form.instance.offer.product
                   
                option_ids = product.additional_options.values('option')                    
                options = Option.objects.filter(pk__in=option_ids)

            except (Product.DoesNotExist, Offer.DoesNotExist):
                pass   
        form.fields['selected_options'].queryset = options
        
class EnhancedInline(admin.StackedInline): 

    formset = EnhancedInlineFormSet
        
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name in self.raw_id_fields:
            kwargs['widget'] = VerboseManyToManyRawIdWidget(db_field.rel)
            return db_field.formfield(**kwargs)
        return super(EnhancedInline, self).formfield_for_manytomany(db_field, request, **kwargs)
        
#        field = super(EnhancedInline, self).formfield_for_manytomany(db_field, request, **kwargs)
#
#        if db_field.name in raw_id_fields:
#            field.help_text = dir(request)
#            if not getattr(request, '_obj_', False):
#                raise Exception('EnhancedInline needs an EnhancedModelAdmin as a parent')
#            if request._obj_ is not None:
#                field.help_text = request._obj_
#            else:
#                field.help_text = 'None'
#
#        return field        
