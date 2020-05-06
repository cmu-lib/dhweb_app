from django import template
import re

register = template.Library()


@register.simple_tag
def url_replace(request, field, value):

    dict_ = request.GET.copy()

    dict_[field] = str(value)

    return dict_.urlencode()


@register.filter
def reduce_lines(value):
    return re.compile(r"^\s+$", re.MULTILINE).sub("", value)
