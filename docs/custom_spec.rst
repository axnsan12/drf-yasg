.. |br| raw:: html

   <br />

########################
Custom schema generation
########################

If the default spec generation does not quite match what you were hoping to achieve, ``drf-yasg`` provides some
custom behavior hooks by default.

.. _custom-spec-excluding-endpoints:

*******************
Excluding endpoints
*******************

You can prevent a view from being included in the Swagger view by setting its class-level ``swagger_schema``
attribute to ``None``, or you can prevent an operation from being included by setting its ``auto_schema`` override
to none in :ref:`@swagger_auto_schema <custom-spec-swagger-auto-schema>`:

.. code-block:: python

   class UserList(APIView):
      swagger_schema = None

      # all methods of the UserList class will be excluded
      ...

   # only the GET method will be shown in Swagger
   @swagger_auto_schema(method='put', auto_schema=None)
   @swagger_auto_schema(methods=['get'], ...)
   @api_view(['GET', 'PUT'])
   def user_detail(request, pk):
      pass

.. _custom-spec-swagger-auto-schema:

**************************************
The ``@swagger_auto_schema`` decorator
**************************************

You can use the :func:`@swagger_auto_schema <.swagger_auto_schema>` decorator on view functions to override
some properties of the generated :class:`.Operation`. For example, in a ``ViewSet``,

.. code-block:: python

   from drf_yasg.utils import swagger_auto_schema

   @swagger_auto_schema(operation_description="partial_update description override", responses={404: 'slug not found'})
   def partial_update(self, request, *args, **kwargs):
      """partial_update method docstring"""
      ...

will override the description of the ``PATCH /article/{id}/`` operation, and document a 404 response with no body and
the given description.

Where you can use the :func:`@swagger_auto_schema <.swagger_auto_schema>` decorator depends on the type of your view:

* for function based ``@api_view``\ s, because the same view can handle multiple methods, and thus represent multiple
  operations, you have to add the decorator multiple times if you want to override different operations:

   .. code-block:: python
   
      from drf_yasg import openapi
      from drf_yasg.utils import swagger_auto_schema
      from rest_framework.decorators import api_view

      from drf_yasg import openapi

      test_param = openapi.Parameter('test', openapi.IN_QUERY, description="test manual param", type=openapi.TYPE_BOOLEAN)
      user_response = openapi.Response('response description', UserSerializer)

      # 'method' can be used to customize a single HTTP method of a view
      @swagger_auto_schema(method='get', manual_parameters=[test_param], responses={200: user_response})
      # 'methods' can be used to apply the same modification to multiple methods
      @swagger_auto_schema(methods=['put', 'post'], request_body=UserSerializer)
      @api_view(['GET', 'PUT', 'POST'])
      def user_detail(request, pk):
          ...

* for class based ``APIView``, ``GenericAPIView`` and non-``ViewSet`` derivatives, you have to decorate the respective
  method of each operation:

   .. code-block:: python

      class UserList(APIView):
         @swagger_auto_schema(responses={200: UserSerializer(many=True)})
         def get(self, request):
            ...

         @swagger_auto_schema(operation_description="description")
         def post(self, request):
            ...

* for ``ViewSet``, ``GenericViewSet``, ``ModelViewSet``, because each viewset corresponds to multiple **paths**, you have
  to decorate the *action methods*, i.e. ``list``, ``create``, ``retrieve``, etc. |br|
  Additionally, ``@action``\ s defined on the viewset, like function based api views, can respond to multiple HTTP
  methods and thus have multiple operations that must be decorated separately:


   .. code-block:: python

      class ArticleViewSet(viewsets.ModelViewSet):
         # method or 'methods' can be skipped because the action only handles a single method (GET)
         @swagger_auto_schema(operation_description='GET /articles/today/')
         @action(detail=False, methods=['get'])
         def today(self, request):
            ...

         @swagger_auto_schema(method='get', operation_description="GET /articles/{id}/image/")
         @swagger_auto_schema(method='post', operation_description="POST /articles/{id}/image/")
         @action(detail=True, methods=['get', 'post'], parser_classes=(MultiPartParser,))
         def image(self, request, id=None):
            ...

         @swagger_auto_schema(operation_description="PUT /articles/{id}/")
         def update(self, request, *args, **kwargs):
            ...

         @swagger_auto_schema(operation_description="PATCH /articles/{id}/")
         def partial_update(self, request, *args, **kwargs):
            ...

.. Tip::

   If you want to customize the generation of a method you are not implementing yourself, you can use
   ``swagger_auto_schema`` in combination with Django's ``method_decorator``:

   .. code-block:: python

      @method_decorator(name='list', decorator=swagger_auto_schema(
          operation_description="description from swagger_auto_schema via method_decorator"
      ))
      class ArticleViewSet(viewsets.ModelViewSet):
         ...

   This allows you to avoid unnecessarily overriding the method.

.. Tip::

   You can go even further and directly decorate the result of ``as_view``, in the same manner you would
   override an ``@api_view`` as described above:

   .. code-block:: python

      decorated_login_view = \
         swagger_auto_schema(
            method='post',
            responses={status.HTTP_200_OK: LoginResponseSerializer}
         )(LoginView.as_view())

      urlpatterns = [
         ...
         url(r'^login/$', decorated_login_view, name='login')
      ]

   This can allow you to avoid skipping an unnecessary *subclass* altogether.

.. Warning::

   However, do note that both of the methods above can lead to unexpected (and maybe surprising) results by
   replacing/decorating methods on the base class itself.


*********************************
Support for SerializerMethodField
*********************************

Schema generation of ``serializers.SerializerMethodField`` is supported in two ways:

1) The :func:`swagger_serializer_method <.swagger_serializer_method>` decorator for the use case where the serializer
   method is using a serializer. e.g.:

   .. code-block:: python

      from drf_yasg.utils import swagger_serializer_method

      class OtherStuffSerializer(serializers.Serializer):
          foo = serializers.CharField()

      class ParentSerializer(serializers.Serializer):
          other_stuff = serializers.SerializerMethodField()
          many_other_stuff = serializers.SerializerMethodField()
          
          @swagger_serializer_method(serializer_or_field=OtherStuffSerializer)
          def get_other_stuff(self, obj):
              return OtherStuffSerializer().data
          
          @swagger_serializer_method(serializer_or_field=OtherStuffSerializer(many=True))
          def get_many_other_stuff(self, obj):
              return OtherStuffSerializer().data


   Note that the ``serializer_or_field`` parameter can accept either a subclass or an instance of ``serializers.Field``.
   
   

2) For simple cases where the method is returning one of the supported types, `Python 3 type hinting`_ of the
   serializer method return value can be used. e.g.:

   .. code-block:: python

      class SomeSerializer(serializers.Serializer):
          some_number = serializers.SerializerMethodField()

          def get_some_number(self, obj) -> float:
              return 1.0

   When return type hinting is not supported, the equivalent ``serializers.Field`` subclass can be used with
   :func:`swagger_serializer_method <.swagger_serializer_method>`:

   .. code-block:: python

      class SomeSerializer(serializers.Serializer):
          some_number = serializers.SerializerMethodField()

          @swagger_serializer_method(serializer_or_field=serializers.FloatField)
          def get_some_number(self, obj):
              return 1.0


********************************
Serializer ``Meta`` nested class
********************************

You can define some per-serializer or per-field options by adding a ``Meta`` class to your ``Serializer`` or
serializer ``Field``, e.g.:

.. code-block:: python

   class WhateverSerializer(Serializer):
      ...

      class Meta:
         ... options here ...

.. _swagger_schema_fields:

The available options are:

   * ``ref_name`` - a string which will be used as the model definition name for this serializer class; setting it to
     ``None`` will force the serializer to be generated as an inline model everywhere it is used. If two serializers
     have the same ``ref_name``, both their usages will be replaced with a reference to the same definition.
     If this option is not specified, all serializers have an implicit name derived from their class name, minus any
     ``Serializer`` suffix (e.g. ``UserSerializer`` -> ``User``, ``SerializerWithSuffix`` -> ``SerializerWithSuffix``)
   * ``swagger_schema_fields`` - a dictionary mapping :class:`.Schema` field names to values. These attributes
     will be set on the :class:`.Schema` object generated from the ``Serializer``. Field names must be python values,
     which are converted to Swagger ``Schema`` attribute names according to :func:`.make_swagger_name`.
     Attribute names and values must conform to the `OpenAPI 2.0 specification <https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#schemaObject>`_.

Suppose you wanted to model an email using a `JSONField` to store the subject and body for performance reasons:

.. code-block:: python

   from django.contrib.postgres.fields import JSONField

   class Email(models.Model):
       # Store data as JSON, but the data should be made up of
       # an object that has two properties, "subject" and "body"
       # Example:
       # {
       #   "subject": "My Title",
       #   "body": "The body of the message.",
       # }
       message = JSONField()

To instruct ``drf-yasg`` to output an OpenAPI schema that matches this, create a custom ``JSONField``:

.. code-block:: python

   class EmailMessageField(serializers.JSONField):
       class Meta:
           swagger_schema_fields = {
               "type": openapi.TYPE_OBJECT,
               "title": "Email",
               "properties": {
                   "subject": openapi.Schema(
                       title="Email subject",
                       type=openapi.TYPE_STRING,
                   ),
                   "body": openapi.Schema(
                       title="Email body",
                       type=openapi.TYPE_STRING,
                   ),
               },
               "required": ["subject", "body"],
            }

   class EmailSerializer(ModelSerializer):
       class Meta:
           model = Email
           fields = "__all__"

       message = EmailMessageField()

.. Warning::

   Overriding a default ``Field`` generated by a ``ModelSerializer`` will also override automatically
   generated validators for that ``Field``.  To add ``Serializer`` validation back in manually, see the relevant
   `DRF Validators`_ and `DRF Fields`_ documentation.

   One example way to do this is to set the ``default_validators`` attribute on a field.

   .. code-block:: python

      class EmailMessageField(serializers.JSONField):
         default_validators = [my_custom_email_validator]
         ...

*************************
Subclassing and extending
*************************


---------------------
``SwaggerAutoSchema``
---------------------

For more advanced control you can subclass :class:`~.inspectors.SwaggerAutoSchema` - see the documentation page
for a list of methods you can override.

You can put your custom subclass to use by setting it on a view method using the
:ref:`@swagger_auto_schema <custom-spec-swagger-auto-schema>` decorator described above, by setting it as a
class-level attribute named ``swagger_schema`` on the view class, or
:ref:`globally via settings <default-class-settings>`.

For example, to generate all operation IDs as camel case, you could do:

.. code-block:: python

   from inflection import camelize

   class CamelCaseOperationIDAutoSchema(SwaggerAutoSchema):
      def get_operation_id(self, operation_keys):
         operation_id = super(CamelCaseOperationIDAutoSchema, self).get_operation_id(operation_keys)
         return camelize(operation_id, uppercase_first_letter=False)


   SWAGGER_SETTINGS = {
      'DEFAULT_AUTO_SCHEMA_CLASS': 'path.to.CamelCaseOperationIDAutoSchema',
      ...
   }

--------------------------
``OpenAPISchemaGenerator``
--------------------------

If you need to control things at a higher level than :class:`.Operation` objects (e.g. overall document structure,
vendor extensions in metadata) you can also subclass :class:`.OpenAPISchemaGenerator` - again, see the documentation
page for a list of its methods.

This custom generator can be put to use by setting it as the :attr:`.generator_class` of a :class:`.SchemaView` using
:func:`.get_schema_view`.

.. _custom-spec-inspectors:

---------------------
``Inspector`` classes
---------------------

For customizing behavior related to specific field, serializer, filter or paginator classes you can implement the
:class:`~.inspectors.FieldInspector`, :class:`~.inspectors.SerializerInspector`, :class:`~.inspectors.FilterInspector`,
:class:`~.inspectors.PaginatorInspector` classes and use them with
:ref:`@swagger_auto_schema <custom-spec-swagger-auto-schema>` or one of the
:ref:`related settings <default-class-settings>`.

A :class:`~.inspectors.FilterInspector` that adds a description to all ``DjangoFilterBackend`` parameters could be
implemented like so:

.. code-block:: python

   class DjangoFilterDescriptionInspector(CoreAPICompatInspector):
      def get_filter_parameters(self, filter_backend):
         if isinstance(filter_backend, DjangoFilterBackend):
            result = super(DjangoFilterDescriptionInspector, self).get_filter_parameters(filter_backend)
            for param in result:
               if not param.get('description', ''):
                  param.description = "Filter the returned list by {field_name}".format(field_name=param.name)

            return result

         return NotHandled

   @method_decorator(name='list', decorator=swagger_auto_schema(
      filter_inspectors=[DjangoFilterDescriptionInspector]
   ))
   class ArticleViewSet(viewsets.ModelViewSet):
      filter_backends = (DjangoFilterBackend,)
      filterset_fields = ('title',)
      ...


A second example, of a :class:`~.inspectors.FieldInspector` that removes the ``title`` attribute from all generated
:class:`.Schema` objects:

.. code-block:: python

   from drf_yasg.inspectors import FieldInspector

   class NoSchemaTitleInspector(FieldInspector):
      def process_result(self, result, method_name, obj, **kwargs):
         # remove the `title` attribute of all Schema objects
         if isinstance(result, openapi.Schema.OR_REF):
            # traverse any references and alter the Schema object in place
            schema = openapi.resolve_ref(result, self.components)
            schema.pop('title', None)

            # no ``return schema`` here, because it would mean we always generate
            # an inline `object` instead of a definition reference

         # return back the same object that we got - i.e. a reference if we got a reference
         return result


   class NoTitleAutoSchema(SwaggerAutoSchema):
      field_inspectors = [NoSchemaTitleInspector] + swagger_settings.DEFAULT_FIELD_INSPECTORS

   class ArticleViewSet(viewsets.ModelViewSet):
      swagger_schema = NoTitleAutoSchema
      ...


.. Note::

   A note on references - :class:`.Schema` objects are sometimes output by reference (:class:`.SchemaRef`); in fact,
   that is how named models are implemented in OpenAPI:

      - in the output swagger document there is a ``definitions`` section containing :class:`.Schema` objects for all
        models
      - every usage of a model refers to that single :class:`.Schema` object - for example, in the ArticleViewSet
        above, all requests and responses containing an ``Article`` model would refer to the same schema definition by a
        ``'$ref': '#/definitions/Article'``

   This is implemented by only generating **one** :class:`.Schema` object for every serializer **class** encountered.

   This means that you should generally avoid view or method-specific ``FieldInspector``\ s if you are dealing with
   references (a.k.a named models), because you can never know which view will be the first to generate the schema
   for a given serializer.

   **IMPORTANT:** nested fields on ``ModelSerializer``\ s that are generated from model ``ForeignKeys`` will always be
   output by value. If you want the by-reference behavior you have to explicitly set the serializer class of nested
   fields instead of letting ``ModelSerializer`` generate one automatically; for example:

   .. code-block:: python

      class OneSerializer(serializers.ModelSerializer):
         class Meta:
            model = SomeModel
            fields = ('id',)


      class AnotherSerializer(serializers.ModelSerializer):
         child = OneSerializer()

         class Meta:
            model = SomeParentModel
            fields = ('id', 'child')

   Another caveat that stems from this is that any serializer named "``NestedSerializer``" will be forced inline
   unless it has a ``ref_name`` set explicitly.


.. _Python 3 type hinting: https://docs.python.org/3/library/typing.html
.. _DRF Validators: https://www.django-rest-framework.org/api-guide/validators/
.. _DRF Fields: https://www.django-rest-framework.org/api-guide/fields/#validators
