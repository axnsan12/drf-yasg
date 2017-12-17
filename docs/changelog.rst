#########
Changelog
#########


*********
**1.0.5**
*********

- **FIX:** fixed a crash caused by having read-only Serializers nested by reference
- **FIX:** removed erroneous backslashes in paths when routes are generated using Django 2
  `path() <https://docs.djangoproject.com/en/2.0/ref/urls/#django.urls.path>`_
- **IMPROVEMENT:** updated ``swagger-ui`` to version 3.7.0

*********
**1.0.4**
*********

- **FIX:** fixed improper generation of YAML references
- **FEATURE:** added ``query_serializer`` parameter to
  :func:`@swagger_auto_schema <.swagger_auto_schema>` (:issue:`16`, :pr:`17`)

*********
**1.0.3**
*********

- **FIX:** fixed bug that caused schema views returned from cache to fail (:issue:`14`)
- **FIX:** disabled automatic generation of response schemas for form operations to avoid confusing errors caused by
  attempting to shove file parameters into Schema objects

*********
**1.0.2**
*********

- First published version
