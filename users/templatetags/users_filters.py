from django import template

register = template.Library()


@register.filter(name='compare_urls')
def zip_lists(compare_value, values):
    if not isinstance(values, list):
        values = [values]
    print(values)
    print(compare_value)
    if any(list(filter(lambda val: val == compare_value, values))):
        return True

    return False
