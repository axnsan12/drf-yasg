from six import binary_type, raise_from, text_type

from collections import OrderedDict

from ruamel import yaml

from .errors import SwaggerValidationError


def _validate_flex(spec):
    try:
        from flex.core import parse as validate_flex
        from flex.exceptions import ValidationError
    except ImportError:
        return

    try:
        validate_flex(spec)
    except ValidationError as ex:
        raise_from(SwaggerValidationError(str(ex)), ex)


def _validate_swagger_spec_validator(spec):
    from swagger_spec_validator.validator20 import validate_spec as validate_ssv
    from swagger_spec_validator.common import SwaggerValidationError as SSVErr
    try:
        validate_ssv(spec)
    except SSVErr as ex:
        raise_from(SwaggerValidationError(str(ex)), ex)


#:
VALIDATORS = {
    'flex': _validate_flex,
    'ssv': _validate_swagger_spec_validator,
}


YAML_MAP_TAG = u'tag:yaml.org,2002:map'


class SaneYamlDumper(yaml.SafeDumper):
    """YamlDumper class usable for dumping ``OrderedDict`` and list instances in a standard way."""

    def ignore_aliases(self, data):
        """Disable YAML references."""
        return True

    def increase_indent(self, flow=False, indentless=False, **kwargs):
        """https://stackoverflow.com/a/39681672

        Indent list elements.
        """
        return super(SaneYamlDumper, self).increase_indent(flow=flow, indentless=False, **kwargs)

    def represent_odict(self, mapping, flow_style=None):  # pragma: no cover
        """https://gist.github.com/miracle2k/3184458

        Make PyYAML output an OrderedDict.

        It will do so fine if you use yaml.dump(), but that generates ugly, non-standard YAML code.

        To use yaml.safe_dump(), you need the following.
        """
        tag = YAML_MAP_TAG
        value = []
        node = yaml.MappingNode(tag, value, flow_style=flow_style)
        if self.alias_key is not None:
            self.represented_objects[self.alias_key] = node
        best_style = True
        if hasattr(mapping, 'items'):
            mapping = mapping.items()
        for item_key, item_value in mapping:
            node_key = self.represent_data(item_key)
            node_value = self.represent_data(item_value)
            if not (isinstance(node_key, yaml.ScalarNode) and not node_key.style):
                best_style = False
            if not (isinstance(node_value, yaml.ScalarNode) and not node_value.style):
                best_style = False
            value.append((node_key, node_value))
        if flow_style is None:
            if self.default_flow_style is not None:
                node.flow_style = self.default_flow_style
            else:
                node.flow_style = best_style
        return node

    def represent_text(self, text):
        if "\n" in text:
            return self.represent_scalar('tag:yaml.org,2002:str', text, style='|')
        return self.represent_scalar('tag:yaml.org,2002:str', text)


SaneYamlDumper.add_representer(binary_type, SaneYamlDumper.represent_text)
SaneYamlDumper.add_representer(text_type, SaneYamlDumper.represent_text)
SaneYamlDumper.add_representer(OrderedDict, SaneYamlDumper.represent_odict)
SaneYamlDumper.add_multi_representer(OrderedDict, SaneYamlDumper.represent_odict)


def yaml_sane_dump(data, binary):
    """Dump the given data dictionary into a sane format:

        * OrderedDicts are dumped as regular mappings instead of non-standard !!odict
        * multi-line mapping style instead of json-like inline style
        * list elements are indented into their parents
        * YAML references/aliases are disabled

    :param dict data: the data to be dumped
    :param bool binary: True to return a utf-8 encoded binary object, False to return a string
    :return: the serialized YAML
    :rtype: str or bytes
    """
    return yaml.dump(data, Dumper=SaneYamlDumper, default_flow_style=False, encoding='utf-8' if binary else None)


class SaneYamlLoader(yaml.SafeLoader):
    def construct_odict(self, node, deep=False):
        self.flatten_mapping(node)
        return OrderedDict(self.construct_pairs(node))


SaneYamlLoader.add_constructor(YAML_MAP_TAG, SaneYamlLoader.construct_odict)


def yaml_sane_load(stream):
    """Load the given YAML stream while preserving the input order for mapping items.

    :param stream: YAML stream (can be a string or a file-like object)
    :rtype: OrderedDict
    """
    return yaml.load(stream, Loader=SaneYamlLoader)
