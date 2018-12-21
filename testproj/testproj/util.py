from django.contrib.staticfiles.templatetags.staticfiles import static
from django.urls import NoReverseMatch
from django.utils.encoding import force_text
from django.utils.functional import lazy


static_lazy = lazy(static, str)
