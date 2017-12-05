class SwaggerError(Exception):
    pass


class SwaggerValidationError(SwaggerError):
    def __init__(self, msg, validator_name, spec, source_codec, *args):
        super(SwaggerValidationError, self).__init__(msg, *args)
        self.validator_name = validator_name
        self.spec = spec
        self.source_codec = source_codec


class SwaggerGenerationError(SwaggerError):
    pass
