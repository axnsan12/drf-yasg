from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.functional import lazy

static_lazy = lazy(static, str)
