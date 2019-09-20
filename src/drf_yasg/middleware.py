from django.http import HttpResponse

from .codecs import _OpenAPICodec
from .errors import SwaggerValidationError


class SwaggerExceptionMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        return None  # pragma: no cover
