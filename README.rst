====================
Django Common
====================

The Django Common project is a set of project independent reusable features.
Currently, the following features have been gathered and are working in Django 1.3:

models
    - TimeStampedModel (adds date_created and date_modified)
fields
    - CountryField
    - MultiSelectField (for selecting multiple choices=)
views 
    - server_error (500 error handler with RequestContext)
admin
    - EnhancedModelAdmin (keeping filter states after edits)
    - EnhancedInline (implements VerboseManyToManyRawIdWidget on m2m fields when name in raw_id_fields)
middleware
    - SSLMiddleware
    - RestrictedAccessMiddleware
    - StripWhitespaceMiddleware
helpers
    - get_setting
    - uniqify_list
    - contains
auth
    - EmailBackend (authenticate user by emailaddress or username)
forms
    - EnhancedForm
    - EnhancedModelForm (combined_fields)
widgets
    - DiggPaginatorWidget
    - admin.VerboseManyToManyRawIdWidget
templatetags
    - common
        * filters: cut, replace, nowhitespace, cleanwhitespace, startswith, endswith
    - development
        * filters: attributes, attributes_formatted, getattribute
templates
    - forms/as_div.html
email
    - send_email_with_template (including an handy directory structure for templates)
pdf
    - content_to_pdf
    - content_to_response
    - render_to_pdf


Upcoming features
============

admin
    - EnhancedInline with Nested inline function

If you have ideas for other features please let me know.

Installation
============

#. Add the `common` directory to your Python path.

#. Add `common` to your INSTALLED_APPS if you want to use templates and templatetags

Configuration
=============


TODOs and BUGS
==============
See: http://github.com/baskoopmans/django-common/issues
