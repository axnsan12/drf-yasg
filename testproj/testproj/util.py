from django.templatetags.static import static
from django.utils.functional import lazy

static_lazy = lazy(static, str)
