# encoding: utf-8

#from email.mime.base import MIMEBase
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import select_template
from django.template import Context, RequestContext, TemplateDoesNotExist

class EmailMultiRelated(EmailMultiAlternatives):
    """
    A version of EmailMessage that makes it easy to send multipart/related
    messages. For example, including text and HTML versions with inline images.
    """
    related_subtype = 'related'

    def __init__(self, *args, **kwargs):
        # self.related_ids = []
        self.related_attachments = []
        return super(EmailMultiRelated, self).__init__(*args, **kwargs)

    def attach_related(self, filename=None, content=None, mimetype=None):
        """
        Attaches a file with the given filename and content. The filename can
        be omitted and the mimetype is guessed, if not provided.

        If the first parameter is a MIMEBase subclass it is inserted directly
        into the resulting message attachments.
        """
        if isinstance(filename, MIMEBase):
            assert content == mimetype == None
            self.related_attachments.append(filename)
        else:
            assert content is not None
            self.related_attachments.append((filename, content, mimetype))

    def attach_related_file(self, path, mimetype=None):
        """Attaches a file from the filesystem."""
        filename = os.path.basename(path)
        content = open(path, 'rb').read()
        self.attach_related(filename, content, mimetype)

    def _create_message(self, msg):
        return self._create_attachments(self._create_related_attachments(self._create_alternatives(msg)))

    def _create_alternatives(self, msg):
        for i, (content, mimetype) in enumerate(self.alternatives):
            if mimetype == 'text/html':
                for filename, _, _ in self.related_attachments:
                    content = re.sub(r'(?<!cid:)%s' % re.escape(filename), 'cid:%s' % filename, content)
                self.alternatives[i] = (content, mimetype)

        return super(EmailMultiRelated, self)._create_alternatives(msg)

    def _create_related_attachments(self, msg):
        encoding = self.encoding or settings.DEFAULT_CHARSET
        if self.related_attachments:
            body_msg = msg
            msg = SafeMIMEMultipart(_subtype=self.related_subtype, encoding=encoding)
            if self.body:
                msg.attach(body_msg)
            for related in self.related_attachments:
                msg.attach(self._create_related_attachment(*related))
        return msg

    def _create_related_attachment(self, filename, content, mimetype=None):
        """
        Convert the filename, content, mimetype triple into a MIME attachment
        object. Adjust headers to use Content-ID where applicable.
        Taken from http://code.djangoproject.com/ticket/4771
        """
        attachment = super(EmailMultiRelated, self)._create_attachment(filename, content, mimetype)
        if filename:
            mimetype = attachment['Content-Type']
            del(attachment['Content-Type'])
            del(attachment['Content-Disposition'])
            attachment.add_header('Content-Disposition', 'inline', filename=filename)
            attachment.add_header('Content-Type', mimetype, name=filename)
            attachment.add_header('Content-ID', '<%s>' % filename)
        return attachment

class TemplatedEmail(EmailMultiAlternatives):
    """
    A version of EmailMultiRelated, EmailMultiAlternatives, EmailMessage that makes it easy to send templated messages.

    https://docs.djangoproject.com/en/dev/topics/email/

    Extra parameters
    - app_name (required)
    - template_name (required)
    - context
    - request (for extra context)

    Send email rendering text and html versions for the specified template name using the context dictionary passed in.
    Arguments are as per django's send_mail apart from template which should be the common path and name of the text and html templates without the extension,
    For example it wil look for the template in order (default Django behaviour for retrieving templates):

    - /myproject/templates/"email/<app_name>/<template_name>/"
    - /myproject/templates/"email/<template_name>/"
    - /myproject/*<app_name>/templates/"email/<app_name>/<template_name>"/ # NOTE: *<app_name> for every installed app
    - /myproject/*<app_name>/templates/"email/<template_name>"/ # NOTE: *<app_name> for every installed app

    """

    def __init__(self, app_name, template_name, subject='', body='', context=None, request=None, from_email=None, to=None, \
                 bcc=None, connection=None, attachments=None, headers=None, alternatives=None, premailer=False):
        self.app_name = app_name
        self.template_name = template_name
        self.premailer = premailer
        to = to if not to or hasattr(to, "__iter__") else [to]
        bcc = bcc if not bcc or hasattr(bcc, "__iter__") else [bcc]
        context = context or {}
        self.context_instance = RequestContext(request, context) if request else Context(context)
        subject = self.render_subject()
        body = self.render_body('txt')
        super(TemplatedEmail, self).__init__(subject, body, from_email, to, bcc, connection, attachments, headers, alternatives)
        self.attach_body('html')

    def render_body(self, type):
        template_list = ['%s/interaction/email/%s/body.%s' % (self.app_name, self.template_name, type), 'interaction/email/%s/body.%s' % (self.template_name, type)]
        template = select_template(template_list)
        return template.render(self.context_instance)

    def render_subject(self):
        template_list = ['%s/interaction/email/%s/subject.txt' % (self.app_name, self.template_name), 'interaction/email/%s/subject.txt' % self.template_name]
        template = select_template(template_list)
        return template.render(self.context_instance).strip()

    def render_premailer(self, html):
        import requests
        data = {
            'html': html,
            'link_query_string': '',
            'remove_ids': False,
            'remove_classes': False,
            'remove_comments': False,
        }
        cleaned_html_url = requests.post('http://premailer.dialect.ca/api/0.1/documents', data).json().get('documents').get('html')
        response = requests.get(cleaned_html_url)
        return response.content

    def attach_body(self, type):
        try:
            # try loading the html body
            body = self.render_body(type)
            if type == 'html':
                content_type = 'text/html'
                if self.premailer:
                    body = self.render_premailer(body)
            else:
                content_type = 'text/txt'
            self.attach_alternative(body, content_type)
        except TemplateDoesNotExist:
            pass


# The subject, message, from_email and recipient_list parameters are required.
#
# subject: A string.
# message: A string.
# from_email: A string.
# recipient_list: A list of strings, each an email address. Each member of recipient_list will see the other recipients in the "To:" field of the email message.
# fail_silently: A boolean. If it's False, send_mail will raise an smtplib.SMTPException. See the smtplib docs for a list of possible exceptions, all of which are subclasses of SMTPException.
# auth_user: The optional username to use to authenticate to the SMTP server. If this isn't provided, Django will use the value of the EMAIL_HOST_USER setting.
# auth_password: The optional password to use to authenticate to the SMTP server. If this isn't provided, Django will use the value of the EMAIL_HOST_PASSWORD setting.
# connection: The optional email backend to use to send the mail. If unspecified, an instance of the default backend will be used. See the documentation on Email backends for more details.



def send_mail_with_template(app_name, template_name, receipents, address_from=getattr(settings, 'DEFAULT_FROM_EMAIL', None), context=None, request=None, attachments=None, fail_silently=False):
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