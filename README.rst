.. role:: python(code)
   :language: python

########################################
drf-yasg - Yet another Swagger generator
########################################

|travis| |nbsp| |codecov| |nbsp| |rtd-badge| |nbsp| |pypi-version|

Generate **real** Swagger/OpenAPI 2.0 specifications from a Django Rest Framework API.

Compatible with

- **Django Rest Framework**: 3.7
- **Django**: 1.11, 2.0
- **Python**: 2.7, 3.4, 3.5, 3.6

**Source**: https://github.com/axnsan12/drf-yasg/

**Documentation**: https://drf-yasg.readthedocs.io/en/latest/

********
Features
********

-  full support for nested Serializers and Schemas
-  response schemas and descriptions
-  model definitions compatible with codegen tools
-  customization hooks at all points in the spec generation process
-  JSON and YAML format for spec
-  bundles latest version of
   `swagger-ui <https://github.com/swagger-api/swagger-ui>`__ and
   `redoc <https://github.com/Rebilly/ReDoc>`__ for viewing the generated documentation
-  schema view is cacheable out of the box
-  generated Swagger schema can be automatically validated by
   `swagger-spec-validator <https://github.com/Yelp/swagger_spec_validator>`__ or
   `flex <https://github.com/pipermerriam/flex>`__

.. figure:: https://raw.githubusercontent.com/axnsan12/drf-yasg/1.0.2/screenshots/redoc-nested-response.png
   :width: 100%
   :figwidth: image
   :alt: redoc screenshot

   **Fully nested request and response schemas.**

.. figure:: https://raw.githubusercontent.com/axnsan12/drf-yasg/1.0.2/screenshots/swagger-ui-list.png
   :width: 100%
   :figwidth: image
   :alt: swagger-ui screenshot

   **Choose between redoc and swagger-ui.**

.. figure:: https://raw.githubusercontent.com/axnsan12/drf-yasg/1.0.2/screenshots/swagger-ui-models.png
   :width: 100%
   :figwidth: image
   :alt: model definitions screenshot

   **Real Model definitions.**


*****************
Table of contents
*****************

.. contents::
   :depth: 4

*****
Usage
*****

0. Installation
===============

The preferred instalation method is directly from pypi:

.. code:: console

   pip install drf-yasg

Additionally, if you want to use the built-in validation mechanisms (see `4. Validation`_), you need to install
some extra requirements:

.. code:: console

   pip install drf-yasg[validation]

.. _readme-quickstart:

1. Quickstart
=============

In ``settings.py``:

.. code:: python

    INSTALLED_APPS = [
        ...
        'drf_yasg',
        ...
    ]

In ``urls.py``:

.. code:: python

    ...
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi

    ...

    schema_view = get_schema_view(
        openapi.Info(
            title="Snippets API",
            default_version='v1',
            description="Test description",
            terms_of_service="https://www.google.com/policies/terms/",
            contact=openapi.Contact(email="contact@snippets.local"),
            license=openapi.License(name="BSD License"),
        ),
        validators=['ssv', 'flex'],
        public=True,
        permission_classes=(permissions.AllowAny,),
    )

    urlpatterns = [
        url(r'^swagger(?P<format>.json|.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
        url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
        url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
        ...
    ]

This exposes 4 cached, validated and publicly available endpoints:

* A JSON view of your API specification at ``/swagger.json``
* A YAML view of your API specification at ``/swagger.yaml``
* A swagger-ui view of your API specification at ``/swagger/``
* A ReDoc view of your API specification at ``/redoc/``

2. Configuration
================

a. ``get_schema_view`` parameters
---------------------------------

- ``info`` - Required. Swagger API Info object
- ``url`` - API base url; if left blank will be deduced from the location the view is served at
- ``patterns`` - passed to SchemaGenerator
- ``urlconf`` - passed to SchemaGenerator
- ``public`` - if False, includes only endpoints the current user has access to
- ``validators`` - a list of validator names to apply on the generated schema; allowed values are ``flex``, ``ssv``
- ``authentication_classes`` - authentication classes for the schema view itself
- ``permission_classes`` - permission classes for the schema view itself

b. ``SchemaView`` options
-------------------------------

-  :python:`SchemaView.with_ui(renderer, cache_timeout, cache_kwargs)` - get a view instance using the
   specified UI renderer; one of ``swagger``, ``redoc``
-  :python:`SchemaView.without_ui(cache_timeout, cache_kwargs)` - get a view instance with no UI renderer;
   same as ``as_cached_view`` with no kwargs
-  :python:`SchemaView.as_cached_view(cache_timeout, cache_kwargs, **initkwargs)` - same as ``as_view``,
   but with optional caching
-  you can, of course, call :python:`as_view` as usual

All of the first 3 methods take two optional arguments,
``cache_timeout`` and ``cache_kwargs``; if present, these are passed on
to Django’s :python:`cached_page` decorator in order to enable caching on the
resulting view. See `3. Caching`_.

c. ``SWAGGER_SETTINGS`` and ``REDOC_SETTINGS``
----------------------------------------------

Additionally, you can include some more settings in your ``settings.py`` file.
The possible settings and their default values are as follows:

.. code:: python

    SWAGGER_SETTINGS = {
        'USE_SESSION_AUTH': True,  # add Django Login and Django Logout buttons, CSRF token to swagger UI page
        'LOGIN_URL': getattr(django.conf.settings, 'LOGIN_URL', None),  # URL for the login button
        'LOGOUT_URL': getattr(django.conf.settings, 'LOGOUT_URL', None),  # URL for the logout button

        # Swagger security definitions to include in the schema;
        # see https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#security-definitions-object
        'SECURITY_DEFINITIONS': {
            'basic': {
                'type': 'basic'
            }
        },

        # url to an external Swagger validation service; defaults to 'http://online.swagger.io/validator/'
        # set to None to disable the schema validation badge in the UI
        'VALIDATOR_URL': '',

        # swagger-ui configuration settings, see https://github.com/swagger-api/swagger-ui/blob/112bca906553a937ac67adc2e500bdeed96d067b/docs/usage/configuration.md#parameters
        'OPERATIONS_SORTER': None,
        'TAGS_SORTER': None,
        'DOC_EXPANSION': 'list',
        'DEEP_LINKING': False,
        'SHOW_EXTENSIONS': True,
        'DEFAULT_MODEL_RENDERING': 'model',
        'DEFAULT_MODEL_DEPTH': 3,
    }

.. code:: python

    REDOC_SETTINGS = {
        # ReDoc UI configuration settings, see https://github.com/Rebilly/ReDoc#redoc-tag-attributes
        'LAZY_RENDERING': True,
        'HIDE_HOSTNAME': False,
        'EXPAND_RESPONSES': 'all',
        'PATH_IN_MIDDLE': False,
    }

3. Caching
==========

Since the schema does not usually change during the lifetime of the django process, there is out of the box support for
caching the schema view in-memory, with some sane defaults:

* caching is enabled by the `cache_page <https://docs.djangoproject.com/en/1.11/topics/cache/#the-per-view-cache>`__
  decorator, using the default Django cache backend, can be changed using the ``cache_kwargs`` argument
* HTTP caching of the response is blocked to avoid confusing situations caused by being shown stale schemas
* if `public` is set to ``False`` on the SchemaView, the cached schema varies on the ``Cookie`` and ``Authorization``
  HTTP headers to enable filtering of visible endpoints according to the authentication credentials of each user; note
  that this means that every user accessing the schema will have a separate schema cached in memory.

4. Validation
=============

Given the numerous methods to manually customzie the generated schema, it makes sense to validate the result to ensure
it still conforms to OpenAPI 2.0. To this end, validation is provided at the generation point using python swagger
libraries, and can be activated by passing :python:`validators=['ssv', 'flex']` to ``get_schema_view``; if the generated
schema is not valid, a :python:`SwaggerValidationError` is raised by the handling codec.

**Warning:** This internal validation can slow down your server.
Caching can mitigate the speed impact of validation.

The provided validation will catch syntactic errors, but more subtle violations of the spec might slip by them. To
ensure compatibility with code generation tools, it is recommended to also employ one or more of the following methods:

``swagger-ui`` validation badge
-------------------------------

Online
^^^^^^

If your schema is publicly accessible, `swagger-ui` will automatically validate it against the official swagger
online validator and display the result in the bottom-right validation badge.

Offline
^^^^^^^

If your schema is not accessible from the internet, you can run a local copy of
`swagger-validator <https://hub.docker.com/r/swaggerapi/swagger-validator/>`_ and set the `VALIDATOR_URL` accordingly:

.. code:: python

    SWAGGER_SETTINGS = {
        ...
        'VALIDATOR_URL': 'http://localhost:8189',
        ...
    }

.. code:: console

    $ docker run --name swagger-validator -d -p 8189:8080 --add-host test.local:10.0.75.1 swaggerapi/swagger-validator
    84dabd52ba967c32ae6b660934fa6a429ca6bc9e594d56e822a858b57039c8a2
    $ curl http://localhost:8189/debug?url=http://test.local:8002/swagger/?format=openapi
    {}

Using ``swagger-cli``
---------------------

https://www.npmjs.com/package/swagger-cli

.. code:: console

    $ npm install -g swagger-cli
    [...]
    $ swagger-cli validate http://test.local:8002/swagger.yaml
    http://test.local:8002/swagger.yaml is valid

Manually on `editor.swagger.io <https://editor.swagger.io/>`__
--------------------------------------------------------------

Importing the generated spec into https://editor.swagger.io/ will automatically trigger validation on it.
This method is currently the only way to get both syntactic and semantic validation on your specification.
The other validators only provide JSON schema-level validation, but miss things like duplicate operation names,
improper content types, etc

5. Code generation
==================

You can use the specification outputted by this library together with
`swagger-codegen <https://github.com/swagger-api/swagger-codegen>`_ to generate client code in your language of choice:

.. code:: console

   $ docker run --rm -v ${PWD}:/local swaggerapi/swagger-codegen-cli generate -i /local/tests/reference.yaml -l javascript -o /local/.codegen/js

See the github page linked above for more details.

**********
Background
**********

``OpenAPI 2.0``/``Swagger`` is a format designed to encode information about a Web API into an easily parsable schema
that can then be used for rendering documentation, generating code, etc.

More details are available on `swagger.io <https://swagger.io/>`__ and on the `OpenAPI 2.0 specification
page <https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md>`__.

From here on, the terms “OpenAPI” and “Swagger” are used interchangeably.

Swagger in Django Rest Framework
================================

Since Django Rest 3.7, there is now `built in support <http://www.django-rest-framework.org/api-guide/schemas/>`__ for
automatic OpenAPI 2.0 schema generation. However, this generation is based on the `coreapi <http://www.coreapi.org/>`__
standard, which for the moment is vastly inferior to OpenAPI in both features and tooling support. In particular,
the OpenAPI codec/compatibility layer provided has a few major problems:

* there is no support for documenting response schemas and status codes
* nested schemas do not work properly
* does not handle more complex fields such as ``FileField``, ``ChoiceField``, …

In short this makes the generated schema unusable for code generation, and mediocre at best for documentation.

Other libraries
===============

There are currently two decent Swagger schema generators that I could
find for django-rest-framework:

* `django-rest-swagger <https://github.com/marcgibbons/django-rest-swagger>`__
* `drf-openapi <https://github.com/limdauto/drf_openapi>`__

Out of the two, ``django-rest-swagger`` is just a wrapper around DRF 3.7 schema generation with an added UI, and
thus presents the same problems. ``drf-openapi`` is a bit more involved and implements some custom handling for response
schemas, but ultimately still falls short in code generation because the responses are plain of lacking support for
named schemas.

Both projects are also currently unmantained.

Documentation, advanced usage
=============================

https://drf-yasg.readthedocs.io/en/latest/

.. |travis| image:: https://img.shields.io/travis/axnsan12/drf-yasg/master.svg
   :target: https://travis-ci.org/axnsan12/drf-yasg
   :alt: Travis CI

.. |codecov| image:: https://img.shields.io/codecov/c/github/axnsan12/drf-yasg/master.svg
   :target: https://codecov.io/gh/axnsan12/drf-yasg
   :alt: Codecov

.. |pypi-version| image:: https://img.shields.io/pypi/v/drf-yasg.svg
   :target: https://pypi.python.org/pypi/drf-yasg/
   :alt: PyPI

.. |rtd-badge| image:: https://img.shields.io/readthedocs/drf-yasg.svg
   :target: https://drf-yasg.readthedocs.io/
   :alt: ReadTheDocs

.. |nbsp| unicode:: 0xA0
   :trim:
