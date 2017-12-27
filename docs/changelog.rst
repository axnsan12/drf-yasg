#########
Changelog
#########


*********
**1.1.1**
*********

- **ADDED:** :ref:`generate_swagger management command <management-command>`
  (:issue:`29`, :pr:`31`, thanks to :ghuser:`beaugunderson`)

*********
**1.1.0**
*********

- **ADDED:** added support for APIs versioned with ``URLPathVersioning`` or ``NamespaceVersioning``
- **ADDED:** added ability to recursively customize schema generation
  :ref:`using pluggable inspector classes <custom-spec-inspectors>`
- **ADDED:** added ``operation_id`` parameter to :func:`@swagger_auto_schema <.swagger_auto_schema>`
- **ADDED:** integration with `djangorestframework-camel-case
  <https://github.com/vbabiy/djangorestframework-camel-case>`_ (:issue:`28`)
- **IMPROVED:** strings, arrays and integers will now have min/max validation attributes inferred from the
  field-level validators
- **FIXED:** fixed a bug that caused ``title`` to never be generated for Schemas; ``title`` is now correctly
  populated from the field's ``label`` property

*********
**1.0.6**
*********

- **FIXED:** Swagger UI "Try it out!" should now work with Django login
- **FIXED:** callable ``default`` values on serializer fields will now be properly called (:pr:`24`, :issue:`25`)
- **IMPROVED:** updated ``swagger-ui`` to version 3.8.0
- **IMPROVED:** ``PrimaryKeyRelatedField`` and ``SlugRelatedField`` will now have
  appropriate types based on the related model (:pr:`26`)
- **IMPROVED:** mock views will now have a bound request even with ``public=False`` (:pr:`23`)

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
