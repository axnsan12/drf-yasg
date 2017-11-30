import json
from collections import OrderedDict

from coreapi.codecs import BaseCodec
from coreapi.compat import force_bytes, urlparse
from drf_swagger.app_settings import swagger_settings
from openapi_codec import encode
from ruamel import yaml

from . import openapi


class SwaggerValidationError(Exception):
    def __init__(self, msg, validator_name, spec, *args) -> None:
        super(SwaggerValidationError, self).__init__(msg, *args)
        self.validator_name = validator_name
        self.spec = spec

    def __str__(self):
        return str(self.validator_name) + ": " + super(SwaggerValidationError, self).__str__()


def _validate_flex(spec):
    from flex.core import parse as validate_flex
    from flex.exceptions import ValidationError
    try:
        validate_flex(spec)
    except ValidationError as ex:
        raise SwaggerValidationError(str(ex), 'flex', spec) from ex


def _validate_swagger_spec_validator(spec):
    from swagger_spec_validator.validator20 import validate_spec as validate_ssv
    from swagger_spec_validator.common import SwaggerValidationError as SSVErr
    try:
        validate_ssv(spec)
    except SSVErr as ex:
        raise SwaggerValidationError(str(ex), 'swagger_spec_validator', spec) from ex


VALIDATORS = {
    'flex': _validate_flex,
    'swagger_spec_validator': _validate_swagger_spec_validator,
    'ssv': _validate_swagger_spec_validator,
}


class _OpenAPICodec(BaseCodec):
    format = 'openapi'

    def __init__(self, validators):
        self._validators = validators

    @property
    def validators(self):
        return self._validators

    def encode(self, document, **options):
        if not isinstance(document, openapi.Swagger):
            raise TypeError('Expected a `openapi.Swagger` instance')

        spec = self.generate_swagger_object(document)
        for validator in self.validators:
            VALIDATORS[validator](spec)
        return force_bytes(self._dump_spec(spec))

    def _dump_spec(self, spec):
        return NotImplementedError("override this method")

    def generate_swagger_object(self, swagger):
        """
        Generates root of the Swagger spec.

        :param openapi.Swagger swagger:
        :return OrderedDict: swagger spec as dict
        """
        parsed_url = urlparse.urlparse(swagger.url)

        spec = OrderedDict()

        spec['swagger'] = '2.0'
        spec['info'] = swagger.info.to_swagger(swagger.version)

        if parsed_url.netloc:
            spec['host'] = parsed_url.netloc
        if parsed_url.scheme:
            spec['schemes'] = [parsed_url.scheme]
        spec['basePath'] = '/'

        spec['paths'] = encode._get_paths_object(swagger)

        spec['securityDefinitions'] = swagger_settings.SECURITY_DEFINITIONS

        return spec


class OpenAPICodecJson(_OpenAPICodec):
    media_type = 'application/openapi+json'

    def _dump_spec(self, spec):
        return json.dumps(spec)


class SaneYamlDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False, **kwargs):
        """https://stackoverflow.com/a/39681672
        Indent list elements.
        """
        return super(SaneYamlDumper, self).increase_indent(flow=flow, indentless=False, **kwargs)

    @staticmethod
    def represent_odict(dump, mapping, flow_style=None):
        """https://gist.github.com/miracle2k/3184458
        Make PyYAML output an OrderedDict.

        It will do so fine if you use yaml.dump(), but that generates ugly,
        non-standard YAML code.

        To use yaml.safe_dump(), you need the following.
        """
        tag = u'tag:yaml.org,2002:map'
        value = []
        node = yaml.MappingNode(tag, value, flow_style=flow_style)
        if dump.alias_key is not None:
            dump.represented_objects[dump.alias_key] = node
        best_style = True
        if hasattr(mapping, 'items'):
            mapping = mapping.items()
        for item_key, item_value in mapping:
            node_key = dump.represent_data(item_key)
            node_value = dump.represent_data(item_value)
            if not (isinstance(node_key, yaml.ScalarNode) and not node_key.style):
                best_style = False
            if not (isinstance(node_value, yaml.ScalarNode) and not node_value.style):
                best_style = False
            value.append((node_key, node_value))
        if flow_style is None:
            if dump.default_flow_style is not None:
                node.flow_style = dump.default_flow_style
            else:
                node.flow_style = best_style
        return node


SaneYamlDumper.add_representer(OrderedDict, SaneYamlDumper.represent_odict)


class OpenAPICodecYaml(_OpenAPICodec):
    media_type = 'application/openapi+yaml'

    def _dump_spec(self, spec):
        return yaml.dump(spec, Dumper=SaneYamlDumper, default_flow_style=False, encoding='utf-8')
