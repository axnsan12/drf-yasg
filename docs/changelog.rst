#########
Changelog
#########

**********
**1.21.8**
**********

**ADDED:** Python 3.11 and 3.12 support (:pr:`891`)
**FIXED:** Fix pkg_resources version lookups for Python 3.9+ (:pr:`891`)

**********
**1.21.7**
**********

*Release date: Jul 20, 2023*

**ADDED:** Added ``drf_yasg.inspectors.query.DrfAPICompatInspector`` (:pr:`857`)
**ADDED:** Added ``DrfAPICompatInspector`` to serve as a replacement ``CoreAPICompatInspector`` (:pr:`857`)
**ADDED:** Allow ``DEFAULT_SPEC_RENDERERS`` default renderers to be overriden in the settings (:pr:`857`)
**FIXED:** Fixed redoc source mapping (:pr:`859`)

**********
**1.21.6**
**********

*Release date: Jun 15, 2023*

**IMPROVED:** Remove required coreapi dependency (:pr:`854`)
**IMPROVED:** Feature: Migrate to PyYAML for yaml generator (:pr:`845`)
**FIXED:** Keep path parameters in their given order (:pr:`841`)
**FIXED:** Provide support for enums in codecs (:pr:`837`)

**********
**1.21.5**
**********

*Release date: Feb 09, 2023*

**ADDED:** Python 3.10 support  (:pr:`818`)
**DEPRECATED:** Python 3.6 support as it's been deprecated by swagger-spec-validator
**FIXED:** RecursiveField resolver (:pr:`822`)

**********
**1.21.4**
**********

*Release date: Sep 26, 2022*

**FIXED:** Remove NullBooleanFields if the django-rest-framework version >= 3.14.0 (:pr:`814`)

**********
**1.21.3**
**********

*Release date: Jul 18, 2022*

**FIXED:** Set generator url for swagger_settings.DEFAULT_API_URL (:pr:`682`)
**FIXED:** Check fields for allow_null attribute (:pr:`688`)
**FIXED:** Encode pytz object field as a string by default (:pr:`717`)
**FIXED:** Handle errors rendering with TemplateHTMLRenderer (:pr:`742`)

**********
**1.21.2**
**********

*Release date: Jul 18, 2022*

**FIXED:** Fixed code block rst syntax in ``README.rst``

**********
**1.21.1**
**********

*Release date: Jul 17, 2022*

**FIXED:** Refer to permission_classes as a tuple (:pr:`678`)
**IMPROVED:** Document drf-extra-fields base64 integration (:pr:`445`)
**ADDED:** Added many support to example code (:pr:`695`)
**ADDED:** Allow specifying response as a reference (:pr:`757`)
**FIXED:** Fix old spelling errors and add a cspell configuration (:pr:`796`)
**FIXED:** Remove universal wheel, python 2 is unsupported (:pr:`782`)
**FIXED:** Fix duration field inspector (:pr:`549`)

**********
**1.21.0**
**********

*Release date: Jul 14, 2022*

- **IMPROVED:** Add utf-8 support to yaml loaders (:pr:`692`)

**********
**1.20.3**
**********

*Release date: Jul 14, 2022*

- **FIXED:** Source mapping in ``redoc.min.js`` (:pr:`778`)
- **FIXED:** Publish action tag pattern in ``publish.yml`` (:pr:`794`)

**********
**1.20.0**
**********

*Release date: Oct 25, 2020*

- **IMPROVED:** updated ``swagger-ui`` to version 3.36.0
- **IMPROVED:** updated ``ReDoc`` to version 2.0.0-rc.40
- **FIXED:** fixed compatibility with Django Rest Framework 3.12
- **FIXED:** fixed compatibility with Python 3.9 typing generics
- **FIXED:** dropped support for obsolete ``django.conf.settings.LOGOUT_URL`` (:pr:`646`)

| **Support was dropped for Python 2.7, DRF 3.8, DRF 3.9.**
| **Requirements are now: Python>=3.6, Django>=2.2, DRF>=3.10**

The 1.18 and 1.19 series was skipped to avoid confusion with the drf-yasg2 fork. I would also like to take this
opportunity to extend my apologies to the community at large for the large gap in the maintenance of drf-yasg
and the problems it has caused.

**********
**1.17.1**
**********

*Release date: Feb 17, 2020*

- **FIXED:** fixed compatibility issue with CurrentUserDefault in Django Rest Framework 3.11
- **FIXED:** respect `USERNAME_FIELD` in `generate_swagger` command (:pr:`486`)

**Support was dropped for Python 3.5, Django 2.0, Django 2.1, DRF 3.7**

**********
**1.17.0**
**********

*Release date: Oct 03, 2019*

- **ADDED:** added `JSONFieldInspector` for `JSONField` support (:pr:`417`)
- **IMPROVED:** updated ``swagger-ui`` to version 3.23.11
- **IMPROVED:** updated ``ReDoc`` to version 2.0.0-rc.14 (:issue:`398`)
- **FIXED:** fixed a type hint support issue (:pr:`428`, :issue:`450`)
- **FIXED:** fixed packaging issue caused by a missing requirement (:issue:`412`)

**********
**1.16.1**
**********

*Release date: Jul 16, 2019*

- **IMPROVED:** better enum type detection for nested `ChoiceField`\ s (:pr:`400`)
- **FIXED:** fixed DRF 3.10 compatibility (:pr:`408`, :issue:`410`, :issue:`411`)

**********
**1.16.0**
**********

*Release date: Jun 13, 2019*

- **ADDED:** added `reference_resolver_class` attribute hook to `SwaggerAutoSchema` (:pr:`350`)
- **ADDED:** added `operation_keys` attribute to `SwaggerAutoSchema`, along with `__init__` parameter (:pr:`355`)
- **FIXED:** fixed potential crash on `issubclass` check without `isclass` check

**********
**1.15.1**
**********

*Release date: Jun 13, 2019*

- **IMPROVED:** updated ``swagger-ui`` to version 3.22.3
- **IMPROVED:** updated ``ReDoc`` to version 2.0.0-rc.8-1
- **FIXED:** fixed an issue with inspection of typing hints on Python 2.7 (:issue:`363`)
- **FIXED:** fixed an issue with inspection of typing hints on Python 3.7 (:issue:`371`)

**Python 3.4 support has been dropped!**

**********
**1.15.0**
**********

*Release date: Apr 01, 2019*

- **ADDED:** added ``is_list_view`` and ``has_list_response`` extension points to ``SwaggerAutoSchema`` (:issue:`331`)
- **IMPROVED:** updated ``swagger-ui`` to version 3.22.0
- **IMPROVED:** updated ``ReDoc`` to version 2.0.0-rc.4
- **FIXED:** ``ListModelMixin`` will now always be treated as a list view (:issue:`306`)
- **FIXED:** non-primitive values in field ``choices`` will now be handled properly (:issue:`340`)

**********
**1.14.0**
**********

*Release date: Mar 04, 2019*

- **IMPROVED:** updated ``swagger-ui`` to version 3.21.0
- **FIXED:** implicit ``ref_name`` collisions will now throw an exception
- **FIXED:** ``RecursiveField`` will now also work as a child of ``ListSerializer`` (:pr:`321`)
- **FIXED:** fixed ``minLength`` and ``maxLength`` for ``ListSerializer`` and ``ListField``
- **FIXED:** the ``items`` property of ``Schema``, ``Parameter`` and ``Items`` objects was renamed to ``items_``; this
  is a *mildly breaking change* and was needed to fix the collision with the ``items`` method of ``dict`` (:pr:`308`)
- **REMOVED:** the ``get_summary`` and ``get_description`` methods have been removed (previously deprecated in 1.12.0)

**********
**1.13.0**
**********

*Release date: Jan 29, 2019*

- **IMPROVED:** type hint inspection is now supported for collections and ``Optional`` (:pr:`272`)
- **IMPROVED:** updated ``swagger-ui`` to version 3.20.5
- **IMPROVED:** updated ``ReDoc`` to version 2.0.0-rc.2
- **DEPRECATED:** quietly dropped support for the ``flex`` validator; it will still work if the library is installed,
  but the setup.py requirement was removed and the validator will be silently skipped if not installed (:issue:`285`)

**********
**1.12.1**
**********

*Release date: Dec 28, 2018*

- **IMPROVED:** updated ``ReDoc`` to version 2.0.0-rc.0
- **FIXED:** management command will now correctly fall back to ``DEFAULT_VERSION`` for mock request
- **FIXED:** fixed bad "raised exception during schema generation" warnings caused by missing ``self`` parameter

**********
**1.12.0**
**********

*Release date: Dec 23, 2018*

- **ADDED:** ``get_security_definitions`` and ``get_security_requirements`` hooks to ``OpenAPISchemaGenerator``
- **ADDED:** added ``get_summary_and_description`` and ``split_summary_from_description`` extension points to
  ``SwaggerAutoSchema`` to allow for better customization
- **IMPROVED:** updated ``swagger-ui`` to version 3.20.4
- **IMPROVED:** paginator ``next`` and ``previous`` fields are now marked as ``x-nullable`` (:issue:`263`)
- **IMPROVED:** added the ``tags`` argument to ``swagger_auto_schema`` (:pr:`259`)
- **IMPROVED:** type of ``enum`` will now be automatically detected from ``ChoiceField`` if all ``choices`` values
  are objects of the same Python class (:pr:`264`)
- **IMPROVED:** ``SwaggerValidationError`` details will now be logged and shown in the exception message
- **FIXED:** user implementations of ``get_queryset``, ``get_parsers`` and ``get_renderers`` will no longer be bypassed
- **FIXED:** fixed handling of lazy objects in user-supplied values
- **FIXED:** ``read_only`` serializer fields will be correctly ignored when generating form parameters (:issue:`261`)
- **FIXED:** fixed incorrect return type from ``UIRenderer`` (:pr:`268`)
- **FIXED:** fixed inconsistent ordering of global ``securityDefinitions`` and ``security`` objects
- **DEPRECATED:** the ``get_summary`` and ``get_description`` extension points have been deprecated in favor of the
  new ``get_summary_and_description``, and will be removed in a future release

**IMPORTANT PACKAGING NOTE**

Starting with this version, the ``setup_requires`` argument was dropped from ``setup.py`` in favor of
``build-system.requires`` in ``pyproject.toml`` . This means that for correctly building or installing from sdist,
you will need to use a PEP517/PEP518 compliant tool (tox>=3.3.0, setuptools>=40, pip>=10.0, pep517.build) or manually
install the build requirements yourself (just ``setuptools`` and ``setuptools-scm``, for now).

Additionally, for correct package version detection, a full git checkout is required when building (this was always the
case). Building without ``.git`` or without ``setuptools-scm`` will result in a distribution with a version like
``drf-yasg-1!0.0.0.dev0+noscm.00000167d19bd859``.

**********
**1.11.1**
**********

*Release date: Nov 29, 2018*

- **IMPROVED:** updated ``swagger-ui`` to version 3.20.1
- **IMPROVED:** updated ``ReDoc`` to version 2.0.0-alpha.41
- **FIXED:** ``minLength`` and ``maxLength`` will now also work for ``ListSerializer`` in addition to ``ListField``
- **FIXED:** ``MultipleChoiceField`` will now use the ``multi`` ``collectionFormat`` where appropriate (:issue:`257`)
- **FIXED:** the ``format``, ``pattern``, ``enum``, ``min_length`` and ``max_length`` attributes of
  ``coreschema.Schema`` will now be persisted into the converted ``openapi.Parameter`` (:issue:`212`, :pr:`233`)

**********
**1.11.0**
**********

*Release date: Oct 14, 2018*

- **ADDED:** ``PERSIST_AUTH``, ``REFETCH_SCHEMA_WITH_AUTH``, ``REFETCH_SCHEMA_ON_LOGOUT``
  settings and related javascript implementation for persisting authentication data to swagger-ui localStorage
- **IMPROVED:** UI-enabled views will now no longer generate the full specification document twice; the HTML part
  of the view will only generate a barebones ``Swagger`` object with no ``paths`` and ``definitions``
- **IMPROVED:** added the ``FETCH_SCHEMA_WITH_QUERY`` setting to enable fetching of the schema document using
  query parameters passed to the UI view (:issue:`208`)
- **IMPROVED:** added support for the very common ``x-nullable`` extension (:issue:`217`)
- **IMPROVED:** extensibility of some classes was improved by adding more extension points, together with more blocks
  for ``swagger-ui.html``/``redoc.html`` and some JavaScript hooks in ``swagger-ui-init.js``
- **FIXED:** removed usage of ``inspect.signature`` on python 2.7 (:issue:`222`)

**********
**1.10.2**
**********

*Release date: Sep 13, 2018*

- **ADDED:** added the ``DISPLAY_OPERATION_ID`` ``swagger-ui`` setting
- **IMPROVED:** updated ``ReDoc`` to version 2.0.0-alpha.38
- **IMPROVED:** Operation summary will now be parsed from multi-line view method docstrings (:issue:`205`)
- **IMPROVED:** ``pattern`` will now work on any field with a ``RegexValidator``
  (would previously not appear on fields with special formats such as ``EmailField``)
- **FIXED:** fixed an issue with ``RelatedFieldInspector`` handling of nested serializers
- **FIXED:** fixed handling of ``reverse_lazy`` in URL settings (:issue:`209`)

**********
**1.10.1**
**********

*Release date: Sep 10, 2018*

- **ADDED:** added the ``SPEC_URL`` setting for controlling the download link in ``swagger-ui`` and ``ReDoc``
- **ADDED:** updated ``ReDoc`` settings (added ``NATIVE_SCROLLBARS`` and ``REQUIRED_PROPS_FIRST``)
- **ADDED:** added ``extra_styles`` and ``extra_scripts`` blocks to ui templates (:issue:`178`)
- **IMPROVED:** updated ``swagger-ui`` to version 3.18.2
- **IMPROVED:** updated ``ReDoc`` to version 2.0.0-alpha.37
- **FIXED:** stopped generating invalid OpenAPI by improper placement of ``readOnly`` Schemas
- **FIXED:** fixed broken CSS when ``USE_SESSION_AUTH=False``
- **FIXED:** fixed implementation of ``operation_summary`` and ``deprecated`` (:pr:`194`, :pr:`198`)
- **FIXED:** fixed a bug related to nested ``typing`` hints (:pr:`195`)
- **FIXED:** removed dependency on ``future`` (:issue:`196`)
- **FIXED:** fixed exceptions logged for fields with ``default=None`` (:issue:`203`)
- **FIXED:** fixed ``request_body=no_body`` handling and related tests (:issue:`188`, :issue:`199`)


**********
**1.10.0**
**********

*Release date: Aug 08, 2018*

- **ADDED:** added ``EXCLUDED_MEDIA_TYPES`` setting for controlling ``produces`` MIME type filtering (:issue:`158`)
- **ADDED:** added support for ``SerializerMethodField``, via the ``swagger_serializer_method`` decorator for the
  method field, and support for Python 3.5 style type hinting of the method field return type
  (:issue:`137`, :pr:`175`, :pr:`179`)

  *NOTE:* in order for this to work, you will have to add the new ``drf_yasg.inspectors.SerializerMethodFieldInspector``
  to your ``DEFAULT_FIELD_INSPECTORS`` array if you changed it from the default value

- **IMPROVED:** updated ``swagger-ui`` to version 3.18.0
- **IMPROVED:** added support for Python 3.7 and Django 2.1 (:pr:`176`)
- **IMPROVED:** ``swagger_schema_fields`` will now also work on serializer ``Field``\ s (:issue:`167`)
- **IMPROVED:** ``ref_name`` collisions will now log a warning message (:issue:`156`)
- **IMPROVED:** added ``operation_summary`` and ``deprecated`` arguments to ``swagger_auto_schema``
  (:issue:`149`, :issue:`173`)
- **FIXED:** made ``swagger_auto_schema`` work with DRF 3.9 ``@action`` mappings (:issue:`177`)

*********
**1.9.2**
*********

*Release date: Aug 03, 2018*

- **IMPROVED:** updated ``swagger-ui`` to version 3.17.6
- **IMPROVED:** updated ``ReDoc`` to version 2.0.0-alpha.32
- **IMPROVED:** added ``--api-version`` argument to the ``generate_swagger`` management command (:pr:`170`)
- **FIXED:** corrected various documentation typos (:pr:`160`, :pr:`162`, :issue:`171`, :pr:`172`)
- **FIXED:** made ``generate_swagger`` work for projects without authentication (:pr:`161`)
- **FIXED:** fixed ``SafeText`` interaction with YAML codec (:issue:`159`)

*********
**1.9.1**
*********

*Release date: Jun 30, 2018*

- **IMPROVED:** added a ``swagger_fake_view`` marker to more easily detect mock views in view methods;
  ``getattr(self, 'swagger_fake_view', False)`` inside a view method like ``get_serializer_class`` will tell you if the
  view instance is being used for swagger schema introspection (:issue:`154`)
- **IMPROVED:** updated ``swagger-ui`` to version 3.17.1
- **IMPROVED:** updated ``ReDoc`` to version 2.0.0-alpha.25
- **FIXED:** fixed wrong handling of duplicate urls in urlconf (:pr:`155`)
- **FIXED:** fixed crash when passing ``None`` as a response override (:issue:`148`)

*********
**1.9.0**
*********

*Release date: Jun 16, 2018*

- **ADDED:** added ``DEFAULT_GENERATOR_CLASS`` setting and ``--generator-class`` argument to the ``generate_swagger``
  management command (:issue:`140`)
- **FIXED:** fixed wrongly required ``'count'`` response field on ``CursorPagination`` (:issue:`141`)
- **FIXED:** fixed some cases where ``swagger_schema_fields`` would not be handled (:pr:`142`)
- **FIXED:** fixed crash when encountering ``coreapi.Fields``\ s without a ``schema`` (:issue:`143`)

*********
**1.8.0**
*********

*Release date: Jun 01, 2018*

- **ADDED:** added a :ref:`swagger_schema_fields <swagger_schema_fields>` field on serializer ``Meta`` classes for
  customizing schema generation (:issue:`132`, :pr:`134`)
- **FIXED:** error responses from schema views are now rendered with ``JSONRenderer`` instead of throwing
  confusing errors (:pr:`130`, :issue:`58`)
- **FIXED:** ``readOnly`` schema fields will now no longer be marked as ``required`` (:pr:`133`)

*********
**1.7.4**
*********

*Release date: May 14, 2018*

- **IMPROVED:** updated ``swagger-ui`` to version 3.14.2
- **IMPROVED:** updated ``ReDoc`` to version 2.0.0-alpha.20
- **FIXED:** ignore ``None`` return from ``get_operation`` to avoid empty ``Path`` objects in output
- **FIXED:** request body is now allowed on ``DELETE`` endpoints (:issue:`118`)

*********
**1.7.3**
*********

*Release date: May 12, 2018*

- **FIXED:** views whose ``__init__`` methods throw exceptions will now be ignored during endpoint enumeration

*********
**1.7.2**
*********

*Release date: May 12, 2018*

- **FIXED:** fixed generation of default ``SECURITY_REQUIREMENTS`` to match documented behavior
- **FIXED:** ordering of ``SECURITY_REQUIREMENTS`` and ``SECURITY_DEFINITIONS`` is now stable

*********
**1.7.1**
*********

*Release date: May 05, 2018*

- **IMPROVED:** updated ``swagger-ui`` to version 3.14.1
- **IMPROVED:** set ``swagger-ui`` ``showCommonExtensions`` to ``True`` by default and add
  ``SHOW_COMMON_EXTENSIONS`` setting key
- **IMPROVED:** set ``min_length=1`` when ``allow_blank=False`` (:pr:`112`, thanks to :ghuser:`elnappo`)
- **FIXED:** made documentation ordering of ``SwaggerDict`` extra attributes stable

*********
**1.7.0**
*********

*Release date: Apr 27, 2018*

- **ADDED:** added integration with `djangorestframework-recursive <https://github.com/heywbj/django-rest-framework-recursive>`_
  (:issue:`109`, :pr:`110`, thanks to :ghuser:`rsichny`)

  *NOTE:* in order for this to work, you will have to add the new ``drf_yasg.inspectors.RecursiveFieldInspector`` to
  your ``DEFAULT_FIELD_INSPECTORS`` array if you changed it from the default value

- **FIXED:** ``SchemaRef`` now supports cyclical references via the ``ignore_unresolved`` argument

*********
**1.6.2**
*********

*Release date: Apr 25, 2018*

- **IMPROVED:** updated ``swagger-ui`` to version 3.13.6
- **IMPROVED:** switched ``ReDoc`` to version 2.0.0-alpha.17 (was 1.21.2); fixes :issue:`107`
- **FIXED:** made documentation ordering of parameters stable for urls with multiple parameters (:issue:`105`, :pr:`106`)
- **FIXED:** fixed crash when using a model ``ChoiceField`` of unknown child type

*********
**1.6.1**
*********

*Release date: Apr 01, 2018*

- **ADDED:** added ``SUPPORTED_SUBMIT_METHODS`` ``swagger-ui`` setting

*********
**1.6.0**
*********

*Release date: Mar 24, 2018*

- **IMPROVED:** ``OAUTH2_REDIRECT_URL`` will now default to the built in ``oauth2-redirect.html`` file

*********
**1.5.1**
*********

*Release date: Mar 18, 2018*

- **IMPROVED:** updated ``swagger-ui`` to version 3.13.0
- **FIXED:** fixed a crash caused by ``serializers.OneToOneRel`` (:pr:`81`, thanks to :ghuser:`ko-pp`)

*********
**1.5.0**
*********

*Release date: Mar 12, 2018*

- **IMPROVED:** ``serializers.HiddenField`` are now hidden (:issue:`78`, :pr:`79`, thanks to :ghuser:`therefromhere`)

  *NOTE:* in order for this to work, you will have to add the new ``drf_yasg.inspectors.HiddenFieldInspector`` to your
  ``DEFAULT_FIELD_INSPECTORS`` array if you changed it from the default value

- **IMPROVED:** type of model field is now detected for ``serializers.SlugRelatedField`` with ``read_only=True``
  (:issue:`82`, :pr:`83`, thanks to :ghuser:`therefromhere`)

*********
**1.4.7**
*********

*Release date: Mar 05, 2018*

- **FIXED:** prevent crashes caused by attempting to delete object attributes which do not exist in the first place
  (:issue:`76`)

*********
**1.4.6**
*********

*Release date: Mar 05, 2018*

- **IMPROVED:** updated ``swagger-ui`` to version 3.12.0
- **IMPROVED:** updated ``ReDoc`` to version 1.21.2

*********
**1.4.5**
*********

*Release date: Mar 05, 2018*

- **FIXED:** fixed an issue with modification of ``swagger_auto_schema`` arguments in-place during introspection, which
  would sometimes cause an incomplete Swagger document to be generated after the first pass (:issue:`74`, :pr:`75`)

*********
**1.4.4**
*********

*Release date: Feb 26, 2018*

- **IMPROVED:** ``type`` for ``ChoiceField`` generated by a ``ModelSerializer`` from a model field with ``choices=...``
  will now be set according to the associated model field (:issue:`69`)
- **FIXED:** ``lookup_field`` and ``lookup_value_regex`` on the same ``ViewSet``  will no longer trigger an exception
  (:issue:`68`)

*********
**1.4.3**
*********

*Release date: Feb 22, 2018*

- **FIXED:** added a missing assignment that would cause the ``default`` argument to ``openapi.Parameter.__init__`` to
  be ignored

*********
**1.4.2**
*********

*Release date: Feb 22, 2018*

- **FIXED:** fixed a bug that causes a ``ModelViewSet`` generated from models with nested ``ForeignKey`` to output
  models named ``Nested`` into the ``definitions`` section (:issue:`59`, :pr:`65`)
- **FIXED:** ``Response`` objects without a ``schema`` are now properly handled when passed through
  ``swagger_auto_schema`` (:issue:`66`)

*********
**1.4.1**
*********

*Release date: Feb 21, 2018*

- **FIXED:** the ``coerce_to_string`` is now respected when setting the type, default value and min/max values of
  ``DecimalField`` in the OpenAPI schema (:issue:`62`)
- **FIXED:** error responses from web UI views are now rendered with ``TemplateHTMLRenderer`` instead of throwing
  confusing errors (:issue:`58`)
- **IMPROVED:** updated ``swagger-ui`` to version 3.10.0
- **IMPROVED:** updated ``ReDoc`` to version 1.21.0

*********
**1.4.0**
*********

*Release date: Feb 04, 2018*

- **ADDED:** added settings for OAuth2 client configuration in ``swagger-ui`` (:issue:`53`)
- **IMPROVED:** updated ``swagger-ui`` to version 3.9.3

*********
**1.3.1**
*********

*Release date: Jan 24, 2018*

- **FIXED:** fixed a bug that would sometimes cause endpoints to wrongly be output as form operations (:issue:`50`)
- **IMPROVED:** added generation of ``produces`` based on renderer classes
- **IMPROVED:** added generation of top-level ``consumes`` and ``produces`` based on
  ``DEFAULT_PARSER_CLASSES`` and ``DEFAULT_RENDERER_CLASSES`` (:issue:`48`)

*********
**1.3.0**
*********

*Release date: Jan 23, 2018*

- **ADDED:** security requirements are now correctly set and can be customized; this should fix problems related
  to authentication in ``swagger-ui`` Try it out!  (:issue:`50`, :pr:`54`)
- **IMPROVED:** updated ``swagger-ui`` to version 3.9.2
- **IMPROVED:** updated ``ReDoc`` to version 1.20.0
- **FIXED:** fixed an exception caused by a warning in get_path_from_regex (:pr:`49`, thanks to :ghuser:`blueyed`)

*********
**1.2.2**
*********

*Release date: Jan 12, 2018*

- **FIXED:** djangorestframework>=3.7.7 is now required because of breaking changes
  (:issue:`44`, :pr:`45`, thanks to :ghuser:`h-hirokawa`)

*********
**1.2.1**
*********

*Release date: Jan 12, 2018*

- Fixed deployment issues

*********
**1.2.0**
*********

*Release date: Jan 12, 2018 (missing from PyPI due to deployment issues)*

- **ADDED:** ``basePath`` is now generated by taking into account the ``SCRIPT_NAME`` variable and the
  longest common prefix of API urls (:issue:`37`, :pr:`42`)
- **IMPROVED:** removed inline scripts and styles from bundled HTML templates to increase CSP compatibility
- **IMPROVED:** improved validation errors and added more assertion sanity checks (:issue:`37`, :issue:`40`)
- **IMPROVED:** improved handling of NamespaceVersioning by excluding endpoints of differing versions
  (i.e. when accessing the schema view for v1, v2 endpoints will not be included in swagger)

*********
**1.1.3**
*********

*Release date: Jan 02, 2018*

- **FIXED:** schema view cache will now always ``Vary`` on the ``Cookie`` and ``Authentication`` (the
  ``Vary`` header was previously only added if ``public`` was set to ``True``) - this fixes issues related to Django
  authentication in ``swagger-ui`` and ``CurrentUserDefault`` values in the schema

*********
**1.1.2**
*********

*Release date: Jan 01, 2018*

- **IMPROVED:** updated ``swagger-ui`` to version 3.8.1
- **IMPROVED:** removed some unneeded static files

*********
**1.1.1**
*********

*Release date: Dec 27, 2017*

- **ADDED:** :ref:`generate_swagger management command <management-command>`
  (:issue:`29`, :pr:`31`, thanks to :ghuser:`beaugunderson`)
- **FIXED:** fixed improper generation of ``\Z`` regex tokens - will now be replaced by ``$``

*********
**1.1.0**
*********

*Release date: Dec 27, 2017*

- **ADDED:** added support for APIs versioned with ``URLPathVersioning`` or ``NamespaceVersioning``
- **ADDED:** added ability to recursively customize schema generation
  :ref:`using plugable inspector classes <custom-spec-inspectors>`
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

*Release date: Dec 23, 2017*

- **FIXED:** Swagger UI "Try it out!" should now work with Django login
- **FIXED:** callable ``default`` values on serializer fields will now be properly called (:pr:`24`, :issue:`25`)
- **IMPROVED:** updated ``swagger-ui`` to version 3.8.0
- **IMPROVED:** ``PrimaryKeyRelatedField`` and ``SlugRelatedField`` will now have
  appropriate types based on the related model (:pr:`26`)
- **IMPROVED:** mock views will now have a bound request even with ``public=False`` (:pr:`23`)

*********
**1.0.5**
*********

*Release date: Dec 18, 2017*

- **FIXED:** fixed a crash caused by having read-only Serializers nested by reference
- **FIXED:** removed erroneous backslashes in paths when routes are generated using Django 2
  `path() <https://docs.djangoproject.com/en/2.0/ref/urls/#django.urls.path>`_
- **IMPROVED:** updated ``swagger-ui`` to version 3.7.0
- **IMPROVED:** ``FileField`` is now generated as an URL or file name in response Schemas
  (:pr:`21`, thanks to :ghuser:`h-hirokawa`)

*********
**1.0.4**
*********

*Release date: Dec 16, 2017*

- **FIXED:** fixed improper generation of YAML references
- **ADDED:** added ``query_serializer`` parameter to
  :func:`@swagger_auto_schema <.swagger_auto_schema>` (:issue:`16`, :pr:`17`)

*********
**1.0.3**
*********

*Release date: Dec 15, 2017*

- **FIXED:** fixed bug that caused schema views returned from cache to fail (:issue:`14`)
- **FIXED:** disabled automatic generation of response schemas for form operations to avoid confusing errors caused by
  attempting to shove file parameters into Schema objects

*********
**1.0.2**
*********

*Release date: Dec 13, 2017*

- First published version
