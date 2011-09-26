# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import select_template
from django.template import Context, RequestContext, TemplateDoesNotExist


def send_mail_with_template(app_name, template_name, receipents, address_from=settings.DEFAULT_FROM_EMAIL, context=None, request=None, attachments=None, fail_silently=False):
    """
    Send email rendering text and html versions for the specified template name using the context dictionary passed in.
    Arguments are as per django's send_mail apart from template which should be the common path and name of the text and html templates without the extension,
    For example it wil look for the template in order:

    Default django behaviour:
        - /myproject/templates/"email/<app_name>/<template_name>/"
        - /myproject/templates/"email/<template_name>/"
        - /myproject/*<app_name>/templates/"email/<app_name>/<template_name>"/ # NOTE: *<app_name> for every installed app
        - /myproject/*<app_name>/templates/"email/<template_name>"/ # NOTE: *<app_name> for every installed app

    """
    if context is None:
        context = {}
    if attachments is None:
        attachments = []

    if request:
        context_instance = RequestContext(request, context)
    else:
        context_instance = Context(context)

    # allow for a single address to be passed in
    if not hasattr(receipents, "__iter__"):
        receipents = [receipents]

    # loads a template passing in vars as context
    render_body = lambda type: select_template(['email/%s/%s/body.%s' % (app_name, template_name, type), 'email/%s/body.%s' % (template_name, type)]).render(context_instance)

    # remder email's subject
    template_list = ['email/%s/%s/subject.txt' % (app_name, template_name), 'email/%s/subject.txt' % template_name]
    subject = select_template(template_list).render(context_instance).strip()

    # create email
    email = EmailMultiAlternatives(subject, render_body('txt'), address_from, receipents)

    try:
        # try loading the html body
        email.attach_alternative(render_body('html'), "text/html")
    except TemplateDoesNotExist:
        pass

    # attachment attachments, what about attach_file?
    for attachment in attachments:
        #raise Exception(attachment)
        email.attach(*attachment)

    # send email
    email.send(fail_silently=fail_silently)