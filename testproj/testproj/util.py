from django.contrib.staticfiles.templatetags.staticfiles import static
from django.urls import NoReverseMatch
from django.utils.encoding import force_text
from django.utils.functional import lazy


def full_url(absolute_path):
    try:
        return "http://test.local:8002" + force_text(absolute_path)
    except NoReverseMatch:
        # if absolute_path is a resolve_lazy, it might point to an invalid name
        # just ignore it if it does
        return "http://test.local:8002/no-reverse-match/"


full_url_lazy = lazy(full_url, str, type(None))
static_lazy = lazy(static, str)
