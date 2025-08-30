""" from django import template

register = template.Library()

@register.filter
def batch(iterable, size):
    l = len(iterable)
    for ndx in range(0, l, size):
        yield iterable[ndx:min(ndx + size, l)] """
        
        
# cda_app/templatetags/filters.py
from django import template

register = template.Library()

@register.filter
def batch(value, arg):
    """
    Batch filter similar to Django's built-in batch filter
    """
    return [value[i:i + arg] for i in range(0, len(value), arg)]
        
        
# cda_app/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})


""" # cda_app/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class}) """