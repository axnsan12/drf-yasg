.. role:: python(code)
   :language: python

.. |br| raw:: html

   <br />

########
Settings
########

Settings are configurable in ``settings.py`` by defining ``SWAGGER_SETTINGS`` or ``REDOC_SETTINGS``.

Example:

**settings.py**

.. code-block:: python

   SWAGGER_SETTINGS = {
       'SECURITY_DEFINITIONS': {
           'basic': {
               'type': 'basic'
           }
       },
       ...
   }

   REDOC_SETTINGS = {
      'LAZY_RENDERING': True,
      ...
   }

The possible settings and their default values are as follows:

********************
``SWAGGER_SETTINGS``
********************


.. _default-class-settings:

Default classes
===============

DEFAULT_AUTO_SCHEMA_CLASS
-------------------------

:class:`~.inspectors.ViewInspector` subclass that will be used by default for generating :class:`.Operation`
objects when iterating over endpoints. Can be overriden by using the `auto_schema` argument of
:func:`@swagger_auto_schema <.swagger_auto_schema>` or by a ``swagger_schema`` attribute on the view class.

**Default**: :class:`drf_yasg.inspectors.SwaggerAutoSchema`

DEFAULT_FIELD_INSPECTORS
------------------------

List of :class:`~.inspectors.FieldInspector` subclasses that will be used by default for inspecting serializers and
serializer fields. Field inspectors given to :func:`@swagger_auto_schema <.swagger_auto_schema>` will be prepended
to this list.

**Default**: ``[``  |br| \
:class:`'drf_yasg.inspectors.CamelCaseJSONFilter' <.inspectors.CamelCaseJSONFilter>`, |br| \
:class:`'drf_yasg.inspectors.ReferencingSerializerInspector' <.inspectors.ReferencingSerializerInspector>`, |br| \
:class:`'drf_yasg.inspectors.RelatedFieldInspector' <.inspectors.RelatedFieldInspector>`, |br| \
:class:`'drf_yasg.inspectors.ChoiceFieldInspector' <.inspectors.ChoiceFieldInspector>`, |br| \
:class:`'drf_yasg.inspectors.FileFieldInspector' <.inspectors.FileFieldInspector>`, |br| \
:class:`'drf_yasg.inspectors.DictFieldInspector' <.inspectors.DictFieldInspector>`, |br| \
:class:`'drf_yasg.inspectors.SimpleFieldInspector' <.inspectors.SimpleFieldInspector>`, |br| \
:class:`'drf_yasg.inspectors.StringDefaultFieldInspector' <.inspectors.StringDefaultFieldInspector>`, |br| \
``]``

DEFAULT_FILTER_INSPECTORS
-------------------------

List of :class:`~.inspectors.FilterInspector` subclasses that will be used by default for inspecting filter backends.
Filter inspectors given to :func:`@swagger_auto_schema <.swagger_auto_schema>` will be prepended to this list.

**Default**: ``[``  |br| \
:class:`'drf_yasg.inspectors.CoreAPICompatInspector' <.inspectors.CoreAPICompatInspector>`, |br| \
``]``

DEFAULT_PAGINATOR_INSPECTORS
----------------------------

List of :class:`~.inspectors.PaginatorInspector` subclasses that will be used by default for inspecting paginators.
Paginator inspectors given to :func:`@swagger_auto_schema <.swagger_auto_schema>` will be prepended to this list.

**Default**: ``[``  |br| \
:class:`'drf_yasg.inspectors.DjangoRestResponsePagination' <.inspectors.DjangoRestResponsePagination>`, |br| \
:class:`'drf_yasg.inspectors.CoreAPICompatInspector' <.inspectors.CoreAPICompatInspector>`, |br| \
``]``

Authorization
=============

USE_SESSION_AUTH
----------------

Enable/disable Django login as an authentication/authorization mechanism. If True, a login/logout button will be
displayed in Swagger UI.

**Default**: :python:`True`

LOGIN_URL
---------

URL for the Django Login action when using `USE_SESSION_AUTH`_.

**Default**: :python:`django.conf.settings.LOGIN_URL`

LOGOUT_URL
----------

URL for the Django Logout action when using `USE_SESSION_AUTH`_.

**Default**: :python:`django.conf.settings.LOGOUT_URL`

SECURITY_DEFINITIONS
--------------------

Swagger security definitions to be included in the specification. |br|
See https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#security-definitions-object.

**Default**:

.. code-block:: python

   'basic': {
      'type': 'basic'
   }

.. _swagger-ui-settings:

Swagger UI settings
===================

Swagger UI configuration settings. |br|
See https://github.com/swagger-api/swagger-ui/blob/112bca906553a937ac67adc2e500bdeed96d067b/docs/usage/configuration.md#parameters.

VALIDATOR_URL
-------------

URL pointing to a swagger-validator instance; used for the validation badge shown in swagger-ui. Can be modified to
point to a local install of `swagger-validator <https://hub.docker.com/r/swaggerapi/swagger-validator/>`_ or
set to ``None`` to remove the badge.

**Default**: :python:`'http://online.swagger.io/validator/'` |br|
*Maps to parameter*: ``validatorUrl``

OPERATIONS_SORTER
-----------------

Sorting order for the operation list of each tag.

* :python:`None`: show in the order returned by the server
* :python:`alpha`: sort alphabetically by path
* :python:`method`: sort by HTTP method

**Default**: :python:`None` |br|
*Maps to parameter*: ``operationsSorter``

TAGS_SORTER
-----------

Sorting order for tagged operation groups.

* :python:`None`: Swagger UI default ordering
* :python:`alpha`: sort alphabetically

**Default**: :python:`None` |br|
*Maps to parameter*: ``tagsSorter``

DOC_EXPANSION
-------------

Controls the default expansion setting for the operations and tags.

* :python:`None`: everything is collapsed
* :python:`list`: only tags are expanded
* :python:`full`: all operations are expanded

**Default**: :python:`'list'` |br|
*Maps to parameter*: ``docExpansion``

DEEP_LINKING
------------

Automatically update the fragment part of the URL with permalinks to the currently selected operation.

**Default**: :python:`False` |br|
*Maps to parameter*: ``deepLinking``

SHOW_EXTENSIONS
---------------

Show vendor extension (``x-..``) fields.

**Default**: :python:`True` |br|
*Maps to parameter*: ``showExtensions``

DEFAULT_MODEL_RENDERING
-----------------------

Controls whether operations show the model structure or the example value by default.

* :python:`model`: show the model fields by default
* :python:`example`: show the example value by default

**Default**: :python:`'model'` |br|
*Maps to parameter*: ``defaultModelRendering``

DEFAULT_MODEL_DEPTH
-------------------

Controls how many levels are expaned by default when showing nested models.

**Default**: :python:`3` |br|
*Maps to parameter*: ``defaultModelExpandDepth``

******************
``REDOC_SETTINGS``
******************

.. _redoc-ui-settings:

ReDoc UI settings
=================

ReDoc UI configuration settings. |br|
See https://github.com/Rebilly/ReDoc#redoc-tag-attributes.

LAZY_RENDERING
--------------

**Default**: :python:`True` |br|
*Maps to attribute*: ``lazy-rendering``

HIDE_HOSTNAME
-------------

**Default**: :python:`False` |br|
*Maps to attribute*: ``hide-hostname``

EXPAND_RESPONSES
----------------

**Default**: :python:`'all'` |br|
*Maps to attribute*: ``expand-responses``

PATH_IN_MIDDLE
--------------

**Default**: :python:`False` |br|
*Maps to attribute*: ``path-in-middle-panel``
