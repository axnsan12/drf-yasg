import argparse
import json
from collections import OrderedDict

from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand

from ... import openapi
from ...app_settings import swagger_settings
from ...codecs import OpenAPICodecJson
from ...generators import OpenAPISchemaGenerator


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'output_file', metavar='output-file',
            nargs='?',
            default='swagger.json',
            type=argparse.FileType('w'),
            help='output path for generated swagger document'
        )
        parser.add_argument(
            '-u', '--url', dest='api_url',
            default='',
            type=str,
            help='base API URL - sets the host, scheme and basePath attributes of the generated document'
        )

    def handle(self, output_file, api_url, *args, **options):
        info = getattr(swagger_settings, 'DEFAULT_INFO', None)
        if not isinstance(info, openapi.Info):
            raise ImproperlyConfigured(
                'settings.SWAGGER_SETTINGS["DEFAULT_INFO"] should be an '
                'import string pointing to an openapi.Info object'
            )

        generator = OpenAPISchemaGenerator(
            info=swagger_settings.DEFAULT_INFO,
            url=api_url
        )

        schema = generator.get_schema(request=None, public=True)
        # TODO: support for YAML?
        codec = OpenAPICodecJson(validators=[])

        swagger_json = codec.encode(schema)
        swagger_json = json.loads(swagger_json.decode('utf-8'), object_pairs_hook=OrderedDict)

        pretty_json = json.dumps(swagger_json, indent=4, ensure_ascii=True)
        output_file.write(pretty_json)
