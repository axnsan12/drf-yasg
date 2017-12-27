import contextlib
import json
import tempfile
from collections import OrderedDict
from io import StringIO

import os
from json import JSONDecodeError

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command

from drf_yasg.codecs import yaml_sane_load


def call_generate_swagger(output_file='-', overwrite=False, format='', api_url='',
                          mock=False, user='', private=False, **kwargs):
    out = StringIO()
    call_command(
        'generate_swagger', stdout=out,
        output_file=output_file, overwrite=overwrite, format=format,
        api_url=api_url, mock=mock, user=user, private=private,
        **kwargs
    )
    return out.getvalue()


def test_reference_schema(db, reference_schema):
    User.objects.create_superuser('admin', 'admin@admin.admin', 'blabla')

    output = call_generate_swagger(format='yaml', api_url='http://test.local:8002/', user='admin')
    output_schema = yaml_sane_load(output)
    assert output_schema == reference_schema


def test_non_public(db):
    output = call_generate_swagger(format='yaml', api_url='http://test.local:8002/', private=True)
    output_schema = yaml_sane_load(output)
    assert len(output_schema['paths']) == 0


def test_no_mock(db):
    output = call_generate_swagger()
    output_schema = json.loads(output, object_pairs_hook=OrderedDict)
    assert len(output_schema['paths']) > 0


def test_file_output(db):
    prefix = os.path.join(tempfile.gettempdir(), tempfile.gettempprefix())
    yaml_file = prefix + 'swagger.yaml'
    json_file = prefix + 'swagger.json'
    other_file = prefix + 'swagger.txt'

    try:
        assert call_generate_swagger(output_file=yaml_file) == ''
        assert call_generate_swagger(output_file=json_file) == ''
        assert call_generate_swagger(output_file=other_file) == ''

        with open(yaml_file) as f:
            content = f.read()
            # YAML is a superset of JSON - that means we have to check that
            # the file is really YAML and not just JSON parsed by the YAML parser
            with pytest.raises(JSONDecodeError):
                json.loads(content)
            output_yaml = yaml_sane_load(content)
        with open(json_file) as f:
            output_json = json.load(f, object_pairs_hook=OrderedDict)
        with open(other_file) as f:
            output_other = json.load(f, object_pairs_hook=OrderedDict)

        assert output_yaml == output_json == output_other
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.remove(yaml_file)
            os.remove(json_file)
            os.remove(other_file)

