from rest_framework.exceptions import APIException


class SwaggerError(APIException):
    pass


class SwaggerValidationError(SwaggerError):
    def __init__(self, msg, errors=None, spec=None, source_codec=None, *args):
        super(SwaggerValidationError, self).__init__(msg, *args)
        self.errors = errors
        self.spec = spec
        self.source_codec = source_codec

        self.detail = {
            'errors': errors,
            'message': msg,
        }


class SwaggerGenerationError(SwaggerError):
    pass
