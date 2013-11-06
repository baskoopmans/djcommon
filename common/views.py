# coding: utf-8

from django.http import HttpResponseNotAllowed
from django.shortcuts import render_to_response
from django.shortcuts import resolve_url
from django.template import RequestContext
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, View


def server_error(request, template_name='500.html'):
    """
    Custom 500 error handler for adding context to the template.
    """
    return render_to_response(template_name, context_instance=RequestContext(request))


class RESTmethod(object):
    methods = ['GET','POST','PUT','DELETE']

    def __call__(self, request, *args, **kwargs):
        callback = getattr(self, request.method.lower(), None)
        if callback:
            return callback(request, *args, **kwargs)
        else:
            return HttpResponseNotAllowed(self.get_allowed_methods())

    def get_allowed_methods(self):
        return [method for method in self.methods if hasattr(self, method.lower())]


class LoginView(FormView):
    form_class = AuthenticationForm

    def form_valid(self, form):
        redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
        auth_login(self.request, form.get_user())
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
        return HttpResponseRedirect(redirect_to)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    @method_decorator(sensitive_post_parameters('password'))
    def dispatch(self, request, *args, **kwargs):
        request.session.set_test_cookie()
        return super(LoginView, self).dispatch(request, *args, **kwargs)


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)