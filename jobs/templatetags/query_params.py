# jobs/templatetags/query_params.py
from django import template
from django.utils.http import urlencode
register = template.Library()

@register.simple_tag(takes_context=True)
def url_params(context, exclude=None, **kwargs):
    """
    Renders current URL query parameters, excluding specified keys,
    and adding/overriding new ones.

    Usage: {% load query_params %}
           <a href="?{% url_params request exclude='page' key1='val1' %}">Link</a>

    'exclude' should be a comma-separated string of keys to remove.
    kwargs are key-value pairs to add/override.
    """
    request = context.get('request')
    if not request:
        return ""

    params = request.GET.copy()
    exclude_keys = [key.strip() for key in (exclude or "").split(',') if key.strip()]

    # Remove excluded keys, handling multi-value keys (like job_time_types)
    keys_to_delete = []
    for key in params:
        if key in exclude_keys:
            keys_to_delete.append(key) # Mark for deletion

    for key in keys_to_delete:
         del params[key] # Delete the key entirely

    # Add/update kwargs
    for key, value in kwargs.items():
        params[key] = value # Set/override single value

    # Special handling if adding 'job_time_types' via kwargs (less common via tag)
    # If you need to ADD multiple job_time_types via the tag, this needs more logic.
    # Usually, JS handles the multi-value toggling.

    return params.urlencode()


register = template.Library()


@register.simple_tag(takes_context=True)
def url_params(context, exclude=None):
    """
    Returns all current request's GET parameters except for the excluded parameter.
    Useful for preserving GET parameters when creating links that modify just one parameter.

    Usage: {% url_params exclude='page' %}
    """
    if exclude is None:
        exclude = []
    elif not isinstance(exclude, list):
        exclude = [exclude]

    query_dict = context['request'].GET.copy()

    for param in exclude:
        if param in query_dict:
            del query_dict[param]

    return query_dict.urlencode()

@register.simple_tag(takes_context=True)
def url_params_excluded_only(context, exclude=None):
    """
    (Definition 3 - NEW) Returns all current request's GET parameters
    except for the excluded parameter(s).
    Intended for use with `as` keyword in template where value is appended manually.
    Functionally the same as Definition 2, just with a different name.
    """
    request = context.get('request')
    if not request:
        return ""

    query_dict = request.GET.copy()

    if exclude:
         if isinstance(exclude, str):
             exclude = [key.strip() for key in exclude.split(',') if key.strip()]
         elif not isinstance(exclude, list):
             exclude = []

         for param in exclude:
             if param in query_dict:
                 query_dict.pop(param, None)

    return query_dict.urlencode()
# --- End Added Third Definition ---