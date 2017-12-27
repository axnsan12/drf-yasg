import json
import logging
import os
import sys
from collections import OrderedDict

from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand

from ... import openapi
from ...app_settings import swagger_settings
from ...codecs import OpenAPICodecJson, OpenAPICodecYaml
from ...generators import OpenAPISchemaGenerator


class Command(BaseCommand):
    help = 'Write the Swagger schema to disk in JSON or YAML format'

    def add_arguments(self, parser):
        parser.add_argument(
            'output_file', metavar='output-file',
            nargs='?',
            default='swagger.json',
            type=str,
            help='output path for generated swagger document, or "-" for stdout'
        )
        parser.add_argument(
            '-f', '--format', dest='format',
            default='', choices=('json', 'yaml'),
            type=str,
            help='output format; if not given, it is guessed from the output file extension and defaults to json'
        )
        parser.add_argument(
            '-u', '--url', dest='api_url',
            default='',
            type=str,
            help='base API URL - sets the host, scheme and basePath attributes of the generated document'
        )

    def write_schema(self, schema, stream, format):
        if format == 'json':
            codec = OpenAPICodecJson(validators=[])
            swagger_json = codec.encode(schema)
            swagger_json = json.loads(swagger_json.decode('utf-8'), object_pairs_hook=OrderedDict)
            pretty_json = json.dumps(swagger_json, indent=4, ensure_ascii=True)
            stream.write(pretty_json)
        elif format == 'yaml':
            codec = OpenAPICodecYaml(validators=[])
            swagger_yaml = codec.encode(schema).decode('utf-8')
            # YAML is already pretty!
            stream.write(swagger_yaml)
        else:
            raise ValueError("unknown format %s" % format)

    def handle(self, output_file, format, api_url, *args, **options):
        # disable logs of WARNING and below
        logging.disable(logging.WARNING)

        info = getattr(swagger_settings, 'DEFAULT_INFO', None)
        if not isinstance(info, openapi.Info):
            raise ImproperlyConfigured(
                'settings.SWAGGER_SETTINGS["DEFAULT_INFO"] should be an '
                'import string pointing to an openapi.Info object'
            )

        generator = OpenAPISchemaGenerator(
            info=info,
            url=api_url or swagger_settings.DEFAULT_API_URL
        )

        schema = generator.get_schema(request=None, public=True)

        if output_file == '-':
            self.write_schema(schema, sys.stdout, format or 'json')
        else:
            with open(output_file, 'x', encoding='utf-8') as stream:
                if not format:
                    if os.path.splitext(output_file)[1] in ('.yml', '.yaml'):
                        format = 'yaml'

                self.write_schema(schema, stream, format or 'json')
