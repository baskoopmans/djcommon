# encoding: utf-8

import re
import urllib

from django import template
from django.template.defaultfilters import stringfilter
from django.template import Template, Variable, TemplateSyntaxError
from django.http import HttpResponse
from django.db.models.query import QuerySet

from django.template.loader_tags import BlockNode, ExtendsNode
from django.template import loader, Context, RequestContext, TextNode

from djcommon.helpers import random_slice_list

register = template.Library()


def get_template(template):
    if isinstance(template, (tuple, list)):
        return loader.select_template(template)
    return loader.get_template(template)

class BlockNotFound(Exception):
    pass

def render_template_block(template, block, context):
    """
    Renders a single block from a template. This template should have previously been rendered.
    """
    return render_template_block_nodelist(template.nodelist, block, context)

def render_template_block_nodelist(nodelist, block, context):
    for node in nodelist:
        if isinstance(node, BlockNode) and node.name == block:
            return node.render(context)
        for key in ('nodelist', 'nodelist_true', 'nodelist_false'):
            if hasattr(node, key):
                try:
                    return render_template_block_nodelist(getattr(node, key), block, context)
                except:
                    pass
    for node in nodelist:
        if isinstance(node, ExtendsNode):
            try:
                return render_template_block(node.get_parent(context), block, context)
            except BlockNotFound:
                pass
    raise BlockNotFound(block)

def render_block_to_string(template_name, block, dictionary=None, context_instance=None):
    """
    Loads the given template_name and renders the given block with the given dictionary as
    context. Returns a string.
    """
    import re

    dictionary = dictionary or {}
    t = get_template(template_name)
    if context_instance:
        context_instance.update(dictionary)
    else:
        context_instance = Context(dictionary)
    template_block = render_template_block(t, block, context_instance)
    return re.sub(r'\s+', ' ', template_block)

def direct_block_to_template(request, template, block, extra_context=None, mimetype=None, **kwargs):
    """
    Render a given block in a given template with any extra URL parameters in the context as
    ``{{ params }}``.
    """
    if extra_context is None:
        extra_context = {}
    dictionary = {'params': kwargs}
    for key, value in extra_context.items():
        if callable(value):
            dictionary[key] = value()
        else:
            dictionary[key] = value
    c = RequestContext(request, dictionary)
    t = get_template(template)
    t.render(c)
    return HttpResponse(render_template_block(t, block, c), mimetype=mimetype)


class RenderAsTemplateNode(template.Node):
    def __init__(self, item_to_be_rendered):
        self.item_to_be_rendered = Variable(item_to_be_rendered)

    def render(self, context):
        try:
            actual_item = self.item_to_be_rendered.resolve(context)
            return Template(actual_item).render(context)
        except template.VariableDoesNotExist:
            return ''


@register.tag
def render_as_template(parser, token):
    bits = token.split_contents()
    if len(bits) !=2:
        raise TemplateSyntaxError("'%s' takes only one argument (a variable representing a template to render)" % bits[0])
    return RenderAsTemplateNode(bits[1])


class RenderTemplateBlockNode(template.Node):
    def __init__(self, template_name, block_name):
        self.template_name = template_name
        self.block_name = block_name

    def render(self, context):
        #template_name = RenderAsTemplateNode(self.template_name).render(context)
        #template = loader.get_template('pages/'+template_name).render(context)
        return render_block_to_string('base.html', self.block_name[1:-1], context)

@register.tag('render_template_block')
def render_template_block_tag(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, template_name, block_name = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError("'%s' takes two arguments (a variable representing a template and a block name)" % tag_name)
    if not (block_name[0] == block_name[-1] and block_name[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument (block_name) should be in quotes" % tag_name)
    return RenderTemplateBlockNode(template_name, block_name)

@register.filter_function
def random_slice(value, arg=1):
    """
    Returns one or more random item(s) from the list or if it's a queryset a new filtered queryset.
    """
    try:
        arg = int(arg)
    except ValueError:
        raise Exception('Invalid argument: %s' % arg)

    if type(value) == QuerySet:
        pks = list(value.values_list('pk', flat=True))
        random_pks = random_slice_list(pks, arg)
        return value.filter(pk__in=random_pks)
    elif type(value) == list:
        return random_slice_list(value, arg)
    else:
        return value[:arg]

@register.filter(name='zip')
def zip_lists(a, b):
    return zip(a, b)

@register.filter
@stringfilter
def cleartags(value, tags):
    tags = [re.escape(tag) for tag in tags.split()]
    tags_re = u'(%s)' % u'|'.join(tags)
    clear_re = re.compile("<\s*%s[^>]*>(.*?)<\s*/\s*\\1>" % tags_re, re.U)
    value = clear_re.sub('', value)
    return value
cleartags.is_safe = True

@register.filter
@stringfilter
def split(str, splitter):
    "Splits the string for with the given splitter"
    return str.split(splitter)

@register.filter
@stringfilter
def cut(value, arg):
    "Removes all values of arg from the given string"
    return value.replace(arg, '')
cut.is_safe = True

@register.filter
@stringfilter
def replace(value, arg):
    "Replaces all arg in the given string"
    arg = arg.split()
    return value.replace(arg[0], arg[1])
replace.is_safe = True

@register.filter
def nowhitespace(value):
    "Removes all whitespace from the given string"
    return u"".join(value.split())
nowhitespace.is_safe = True

@register.filter
def cleanwhitespace(value):
    "Removes all multiple whitespace from the given string"
    return u" ".join(value.split())
cleanwhitespace.is_safe = True

@register.filter
@stringfilter
def startswith(value, arg):
    "Checks if the given string starts with arg"
    return value.startswith(arg)

@register.filter
@stringfilter
def endswith(value, arg):
    "Checks if the given string ends with arg"
    return value.endswith(arg)

@register.filter
@stringfilter
def urlunquote(value):
    "Unquote a url"
    return urllib.unquote(value)
