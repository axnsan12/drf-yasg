import json

from django.test import TestCase
from ruamel import yaml

from drf_swagger import openapi, codecs
from drf_swagger.generators import OpenAPISchemaGenerator


class SchemaGeneratorTest(TestCase):
    def setUp(self):
        self.generator = OpenAPISchemaGenerator(
            info=openapi.Info("Test generator", "v1"),
            version="v2",
        )
        self.codec_json = codecs.OpenAPICodecJson(['flex', 'ssv'])
        self.codec_yaml = codecs.OpenAPICodecYaml(['ssv', 'flex'])

    def _validate_schema(self, swagger):
        from flex.core import parse as validate_flex
        from swagger_spec_validator.validator20 import validate_spec as validate_ssv

        validate_flex(swagger)
        validate_ssv(swagger)

    def test_schema_generates_without_errors(self):
        self.generator.get_schema(None, True)

    def test_schema_is_valid(self):
        swagger = self.generator.get_schema(None, True)
        self.codec_yaml.encode(swagger)

    def test_invalid_schema_fails(self):
        bad_generator = OpenAPISchemaGenerator(
            info=openapi.Info(
                "Test generator", "v1",
                contact=openapi.Contact(name=69, email=[])
            ),
            version="v2",
        )

        swagger = bad_generator.get_schema(None, True)
        with self.assertRaises(codecs.SwaggerValidationError):
            self.codec_json.encode(swagger)

    def test_json_codec_roundtrip(self):
        swagger = self.generator.get_schema(None, True)
        json_bytes = self.codec_json.encode(swagger)
        self._validate_schema(json.loads(json_bytes.decode('utf-8')))

    def test_yaml_codec_roundtrip(self):
        swagger = self.generator.get_schema(None, True)
        json_bytes = self.codec_yaml.encode(swagger)
        self._validate_schema(yaml.safe_load(json_bytes.decode('utf-8')))


class SchemaTest(TestCase):
    def setUp(self):
        self.generator = OpenAPISchemaGenerator(
            info=openapi.Info("Test generator", "v1"),
            version="v2",
        )
        self.codec_json = codecs.OpenAPICodecJson(['flex', 'ssv'])
        self.codec_yaml = codecs.OpenAPICodecYaml(['ssv', 'flex'])

        self.swagger = self.generator.get_schema(None, True)
        json_bytes = self.codec_yaml.encode(self.swagger)
        self.swagger_dict = yaml.safe_load(json_bytes.decode('utf-8'))

    def test_paths_not_empty(self):
        self.assertTrue(bool(self.swagger_dict['paths']))

    def test_appropriate_status_codes(self):
        snippets_list = self.swagger_dict['paths']['/snippets/']
        self.assertTrue('200' in snippets_list['get']['responses'])
        self.assertTrue('201' in snippets_list['post']['responses'])
        snippets_detail = self.swagger_dict['paths']['/snippets/{id}/']
        self.assertTrue('200' in snippets_detail['get']['responses'])
        self.assertTrue('200' in snippets_detail['put']['responses'])
        self.assertTrue('200' in snippets_detail['patch']['responses'])
        self.assertTrue('204' in snippets_detail['delete']['responses'])

    def test_operation_docstrings(self):
        snippets_list = self.swagger_dict['paths']['/snippets/']
        self.assertEqual(snippets_list['get']['description'], "SnippetList classdoc")
        self.assertEqual(snippets_list['post']['description'], "post method docstring")
        snippets_detail = self.swagger_dict['paths']['/snippets/{id}/']
        self.assertEqual(snippets_detail['get']['description'], "SnippetDetail classdoc")
        self.assertEqual(snippets_detail['put']['description'], "put class docstring")
        self.assertEqual(snippets_detail['patch']['description'], "patch method docstring")
        self.assertEqual(snippets_detail['delete']['description'], "delete method docstring")
