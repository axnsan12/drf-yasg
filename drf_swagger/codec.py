import json
from collections import OrderedDict

from coreapi.compat import force_bytes
from ruamel import yaml

from drf_swagger.app_settings import swagger_settings
from drf_swagger.errors import SwaggerValidationError
from . import openapi


def _validate_flex(spec, codec):
    from flex.core import parse as validate_flex
    from flex.exceptions import ValidationError
    try:
        validate_flex(spec)
    except ValidationError as ex:
        raise SwaggerValidationError(str(ex), 'flex', spec, codec) from ex


def _validate_swagger_spec_validator(spec, codec):
    from swagger_spec_validator.validator20 import validate_spec as validate_ssv
    from swagger_spec_validator.common import SwaggerValidationError as SSVErr
    try:
        validate_ssv(spec)
    except SSVErr as ex:
        raise SwaggerValidationError(str(ex), 'swagger_spec_validator', spec, codec) from ex


VALIDATORS = {
    'flex': _validate_flex,
    'swagger_spec_validator': _validate_swagger_spec_validator,
    'ssv': _validate_swagger_spec_validator,
}


class _OpenAPICodec(object):
    format = 'openapi'
    media_type = None

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
            VALIDATORS[validator](spec, self)
        return force_bytes(self._dump_dict(spec))

    def encode_error(self, err):
        return force_bytes(self._dump_dict(err))

    def _dump_dict(self, spec):
        return NotImplementedError("override this method")

    def generate_swagger_object(self, swagger):
        """
        Generates root of the Swagger spec.

        :param openapi.Swagger swagger:
        :return OrderedDict: swagger spec as dict
        """
        swagger.security_definitions = swagger_settings.SECURITY_DEFINITIONS
        return swagger


class OpenAPICodecJson(_OpenAPICodec):
    media_type = 'application/openapi+json'

    def _dump_dict(self, spec):
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


SaneYamlDumper.add_multi_representer(OrderedDict, SaneYamlDumper.represent_odict)


class OpenAPICodecYaml(_OpenAPICodec):
    media_type = 'application/openapi+yaml'

    def _dump_dict(self, spec):
        return yaml.dump(spec, Dumper=SaneYamlDumper, default_flow_style=False, encoding='utf-8')
