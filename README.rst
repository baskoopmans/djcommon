==========================
Django Common aka djcommon
==========================

The Django Common (djcommon) project is a set of project independent reusable features easy to use while
developing with the Django Framework - https://www.djangoproject.com/.

Features
========

Currently, the following features have been gathered and are working in Django 1.3+

models
    - TimeStampedModel (adds date_created and date_modified)

fields
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
    - get_setting (shortcut for getattr(settings, 'SITE_ID'))
    - uniqify_list
    - contains

auth
    - EmailBackend (authenticate user by email address or username)

forms
    - EnhancedForm
    - EnhancedModelForm (combined_fields)

widgets
    - DiggPaginatorWidget
    - admin.VerboseManyToManyRawIdWidget

template
    - get_available_templates
    - get_template_choices
    - CachedNode
    - ContextUpdatingNode
    - CachedContextUpdatingNode

templatetags
    - common
        * filters: cleartags, cut, replace, nowhitespace, cleanwhitespace, startswith, endswith
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

xml
    - fast_iter


TODO
====

admin
    - EnhancedInline with Nested inline function

If you have ideas for other features please let me know.

Installation
============

#. pip install djcommon

#. Add `djcommon` to your INSTALLED_APPS if you want to use templates and templatetags


TODOs and BUGS
==============
See: http://github.com/baskoopmans/djcommon/issues
