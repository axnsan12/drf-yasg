#########
Changelog
#########


*********
**1.0.5**
*********

- **FIXED:** fixed a crash caused by having read-only Serializers nested by reference
- **FIXED:** removed erroneous backslashes in paths when routes are generated using Django 2
  `path() <https://docs.djangoproject.com/en/2.0/ref/urls/#django.urls.path>`_
- **IMPROVED:** updated ``swagger-ui`` to version 3.7.0
- **IMPROVED:** ``FileField`` is now generated as an URL or file name in response Schemas
  (:pr:`21`, thanks to :ghuser:`h-hirokawa`)

*********
**1.0.4**
*********

- **FIXED:** fixed improper generation of YAML references
- **ADDED:** added ``query_serializer`` parameter to
  :func:`@swagger_auto_schema <.swagger_auto_schema>` (:issue:`16`, :pr:`17`)

*********
**1.0.3**
*********

- **FIXED:** fixed bug that caused schema views returned from cache to fail (:issue:`14`)
- **FIXED:** disabled automatic generation of response schemas for form operations to avoid confusing errors caused by
  attempting to shove file parameters into Schema objects

*********
**1.0.2**
*********

- First published version
