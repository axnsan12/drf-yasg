import json

from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

from .codec import _OpenAPICodec
from drf_swagger.errors import SwaggerValidationError


class SwaggerExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, SwaggerValidationError):
            err = {'errors': {exception.validator_name: str(exception)}}
            codec = exception.source_codec
            if isinstance(codec, _OpenAPICodec):
                err = codec.encode_error(err)
                content_type = codec.media_type
                return HttpResponse(err, status=500, content_type=content_type)

        return None
