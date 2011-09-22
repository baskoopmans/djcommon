====================
Django Common
====================

The Django Common project is a set of project independant reusable features.
Currently, the following feautres have been gathered and are working in Django 1.3:

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
middleware
    - SSLMiddleware
    - RestrictedAccessMiddleware
    - StripWhitespaceMiddleware
views 
    - server_error (500 error handler with RequestContext)
auth
    - EmailBackend (authenticate user by emailaddress or username)
forms
    - EnhancedForm
    - EnhancedModelForm (combined_fields)
pdf
    - content_to_pdf
    - content_to_response
    - render_to_pdf

If you have ideas for other features please let us know.

Installation
============

#. Add the `common` directory to your Python path.

#. Add `common` to your INSTALLED_APPS if you want to use templates and templatetags

Configuration
=============


TODOs and BUGS
==============
See: http://github.com/baskoopmans/django-common/issues
