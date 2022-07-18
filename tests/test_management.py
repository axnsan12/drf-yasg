import json
import os
import random
import string
import tempfile
from collections import OrderedDict

import pytest

from drf_yasg import openapi
from drf_yasg.codecs import yaml_sane_load
from drf_yasg.generators import OpenAPISchemaGenerator


def test_reference_schema(call_generate_swagger, db, reference_schema):
    output = call_generate_swagger(format='yaml', api_url='http://test.local:8002/', user='admin')
    output_schema = yaml_sane_load(output)
    assert output_schema == reference_schema


def test_non_public(call_generate_swagger, db):
    output = call_generate_swagger(format='yaml', api_url='http://test.local:8002/', private=True)
    output_schema = yaml_sane_load(output)
    assert len(output_schema['paths']) == 0


def test_no_mock(call_generate_swagger, db):
    output = call_generate_swagger()
    output_schema = json.loads(output, object_pairs_hook=OrderedDict)
    assert len(output_schema['paths']) > 0


class EmptySchemaGenerator(OpenAPISchemaGenerator):
    def get_paths(self, endpoints, components, request, public):
        return openapi.Paths(paths={}), ''


def test_generator_class(call_generate_swagger, db):
    output = call_generate_swagger(generator_class_name='test_management.EmptySchemaGenerator')
    output_schema = json.loads(output, object_pairs_hook=OrderedDict)
    assert len(output_schema['paths']) == 0


def silent_remove(filename):
    try:
        os.remove(filename)
    except OSError:
        pass


def test_file_output(call_generate_swagger, db):
    prefix = os.path.join(tempfile.gettempdir(), tempfile.gettempprefix())
    name = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
    yaml_file = prefix + name + '.yaml'
    json_file = prefix + name + '.json'
    other_file = prefix + name + '.txt'

    try:
        # when called with output file nothing should be written to stdout
        assert call_generate_swagger(output_file=yaml_file) == ''
        assert call_generate_swagger(output_file=json_file) == ''
        assert call_generate_swagger(output_file=other_file) == ''

        with pytest.raises(OSError):
            # a second call should fail because file exists
            call_generate_swagger(output_file=yaml_file)

        # a second call with overwrite should still succeed
        assert call_generate_swagger(output_file=json_file, overwrite=True) == ''

        with open(yaml_file) as f:
            content = f.read()
            # YAML is a superset of JSON - that means we have to check that
            # the file is really YAML and not just JSON parsed by the YAML parser
            with pytest.raises(ValueError):
                json.loads(content)
            output_yaml = yaml_sane_load(content)
        with open(json_file) as f:
            output_json = json.load(f, object_pairs_hook=OrderedDict)
        with open(other_file) as f:
            output_other = json.load(f, object_pairs_hook=OrderedDict)

        assert output_yaml == output_json == output_other
    finally:
        silent_remove(yaml_file)
        silent_remove(json_file)
        silent_remove(other_file)
