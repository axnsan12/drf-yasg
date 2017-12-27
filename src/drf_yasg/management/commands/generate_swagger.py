import argparse

from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand

from ...app_settings import swagger_settings
from ...codecs import OpenAPICodecJson
from ...generators import OpenAPISchemaGenerator
from ...openapi import Info


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('output_file',
                            nargs='?',
                            default='swagger.json',
                            type=argparse.FileType('wb'))

    def handle(self, output_file, *args, **options):
        if (not swagger_settings.DEFAULT_INFO or not
                swagger_settings.DEFAULT_API_URL):
            raise ImproperlyConfigured(
                'Please set DEFAULT_INFO, DEFAULT_VERSION, and '
                'DEFAULT_API_URL')

        info = Info(
            title=swagger_settings.DEFAULT_INFO,
            default_version=swagger_settings.DEFAULT_VERSION)

        generator = OpenAPISchemaGenerator(
            info=info,
            version=swagger_settings.DEFAULT_VERSION,
            url=swagger_settings.DEFAULT_API_URL)

        schema = generator.get_schema(request=None, public=True)
        codec = OpenAPICodecJson(validators=[])
        json = codec.encode(schema)

        output_file.write(json)
