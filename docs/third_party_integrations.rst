########################
Third Party Integrations
########################

****************
drf-extra-fields
****************

Integration with `drf-extra-fields <https://github.com/Hipo/drf-extra-fields>`_ has a problem
with Base64 fields. By default, ``drf-yasg2`` will generate Base64 file or image fields as
Readonly and not required in the OpenAPI schema. Here is a workaround to mark required Base64
fields correctly.

.. code:: python

    class PDFBase64FileField(Base64FileField):
        ALLOWED_TYPES = ['pdf']

        class Meta:
            swagger_schema_fields = {
                'type': 'string',
                'title': 'File Content',
                'description': 'Content of the file base64 encoded',
                'read_only': False  # <-- FIX
            }

        def get_file_extension(self, filename, decoded_file):
            try:
                PyPDF2.PdfFileReader(io.BytesIO(decoded_file))
            except PyPDF2.utils.PdfReadError as e:
                logger.warning(e)
            else:
                return 'pdf'
