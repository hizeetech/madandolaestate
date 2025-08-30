# cda_app/templatetags/batch_filter.py
from django import template

register = template.Library()

@register.filter
def batch(iterable, n=1):
    """
    Batch filter implementation
    Example: {% for group in items|batch:3 %}
    """
    length = len(iterable)
    for i in range(0, length, n):
        yield iterable[i:i + n]