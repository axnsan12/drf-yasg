import json
import logging
import os
from collections import OrderedDict

from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView

from ... import openapi
from ...app_settings import swagger_settings
from ...codecs import OpenAPICodecJson, OpenAPICodecYaml
from ...generators import OpenAPISchemaGenerator


class Command(BaseCommand):
    help = 'Write the Swagger schema to disk in JSON or YAML format.'

    def add_arguments(self, parser):
        parser.add_argument(
            'output_file', metavar='output-file',
            nargs='?',
            default='-',
            type=str,
            help='Output path for generated swagger document, or "-" for stdout.'
        )
        parser.add_argument(
            '-o', '--overwrite',
            default=False, action='store_true',
            help='Overwrite the output file if it already exists. '
                 'Default behavior is to stop if the output file exists.'
        )
        parser.add_argument(
            '-f', '--format', dest='format',
            default='', choices=('json', 'yaml'),
            type=str,
            help='Output format. If not given, it is guessed from the output file extension and defaults to json.'
        )
        parser.add_argument(
            '-u', '--url', dest='api_url',
            default='',
            type=str,
            help='Base API URL - sets the host and scheme attributes of the generated document.'
        )
        parser.add_argument(
            '-m', '--mock-request', dest='mock',
            default=False, action='store_true',
            help='Use a mock request when generating the swagger schema. This is useful if your views or serializers'
                 'depend on context from a request in order to function.'
        )
        parser.add_argument(
            '--user', dest='user',
            default='',
            help='Username of an existing user to use for mocked authentication. This option implies --mock-request.'
        )
        parser.add_argument(
            '-p', '--private',
            default=False, action="store_true",
            help='Hides endpoints not accesible to the target user. If --user is not given, only shows endpoints that '
                 'are accesible to unauthenticated users.\n'
                 'This has the same effect as passing public=False to get_schema_view() or '
                 'OpenAPISchemaGenerator.get_schema().\n'
                 'This option implies --mock-request.'
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
        else:  # pragma: no cover
            raise ValueError("unknown format %s" % format)

    def get_mock_request(self, url, format, user=None):
        factory = APIRequestFactory()

        request = factory.get(url + '/swagger.' + format)
        if user is not None:
            force_authenticate(request, user=user)
        request = APIView().initialize_request(request)
        return request

    def handle(self, output_file, overwrite, format, api_url, mock, user, private, *args, **options):
        # disable logs of WARNING and below
        logging.disable(logging.WARNING)

        info = getattr(swagger_settings, 'DEFAULT_INFO', None)
        if not isinstance(info, openapi.Info):
            raise ImproperlyConfigured(
                'settings.SWAGGER_SETTINGS["DEFAULT_INFO"] should be an '
                'import string pointing to an openapi.Info object'
            )

        if not format:
            if os.path.splitext(output_file)[1] in ('.yml', '.yaml'):
                format = 'yaml'
        format = format or 'json'

        api_url = api_url or swagger_settings.DEFAULT_API_URL

        user = User.objects.get(username=user) if user else None
        mock = mock or private or (user is not None)
        if mock and not api_url:
            raise ImproperlyConfigured(
                '--mock-request requires an API url; either provide '
                'the --url argument or set the DEFAULT_API_URL setting'
            )

        request = self.get_mock_request(api_url, format, user) if mock else None

        generator = OpenAPISchemaGenerator(
            info=info,
            url=api_url
        )
        schema = generator.get_schema(request=request, public=not private)

        if output_file == '-':
            self.write_schema(schema, self.stdout, format)
        else:
            # normally this would be easily done with open(mode='x'/'w'),
            # but python 2 is a pain in the ass as usual
            flags = os.O_CREAT | os.O_WRONLY
            flags = flags | (os.O_TRUNC if overwrite else os.O_EXCL)
            with os.fdopen(os.open(output_file, flags), "w") as stream:
                self.write_schema(schema, stream, format)
