from django import template

register = template.Library()

@register.filter
def calculate_start_index(value, per_page, current_page):
    """
    Custom template filter to calculate the start index of items on the current page.
    Takes the total count, items per page, and current page number as input.
    """
    if value > 0:
        return (current_page - 1) * per_page + 1
    return 0

