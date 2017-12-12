.. |br| raw:: html

   <br />

########################
Custom schema generation
########################

If the default spec generation does not quite match what you were hoping to achieve, ``drf-swagger`` provides some
custom behavior hooks by default.

*********************
Swagger spec overview
*********************

This library generates OpenAPI 2.0 documents. The authoritative specification for this document's structure will always
be the official documentation over at `swagger.io <https://swagger.io/>`__ and the `OpenAPI 2.0 specification
page <https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md>`__.

Beause the above specifications are a bit heavy and convoluted, here is a general overview of how the specification
is structured, starting from the root ``Swagger`` object.

* :class:`.Swagger` object
   + ``info``, ``schemes``, ``securityDefinitions`` and other informative attributes
   + ``paths``: :class:`.Paths` object
      A list of all the paths in the API in the form of a mapping

      - ``{path}``: :class:`.PathItem` - each :class:`.PathItem` has multiple operations keyed by method
         * ``{http_method}``: :class:`.Operation`
            Each operation is thus uniquely identified by its ``(path, http_method)`` combination,
            e.g. ``GET /articles/``, ``POST /articles/``, etc.
         * ``parameters``: [:class:`.Parameter`] - and a list of path parameters
   + ``definitions``: named Models
      A list of all the named models in the API in the form of a mapping

      - ``{ModelName}``: :class:`.Schema`

* :class:`.Operation` contains the following information about each operation:
   + ``parameters``: [:class:`.Parameter`]
      A list of all the *query*, *header* and *form* parameters accepted by the operation.

      - there can also be **at most one** body parameter whose structure is represented by a
        :class:`.Schema` or a reference to one (:class:`.SchemaRef`)
   + ``responses``: :class:`.Responses`
      A list of all the possible responses the operation is expected to return. Each response can optionally have a
      :class:`.Schema` which describes the structure of its body.

      - ``{status_code}``: :class:`.Response` - mapping of status code to response definition

   + ``operationId`` - should be unique across all operations
   + ``tags`` - used to group operations in the listing

It is interesting to note that the main difference between ``Parameter`` and ``Schema`` is that Schemas can nest other
Schemas, while Parameters are "primitives" and cannot contain other Parameters. The only exception are ``body``
Parameters, which can contain a Schema.

**************************************
The ``@swagger_auto_schema`` decorator
**************************************

You can use the :func:`@swagger_auto_schema <.swagger_auto_schema>` decorator on view functions to override
some properties of the generated :class:`.Operation`. For example, in a ``ViewSet``,

.. code:: python

   @swagger_auto_schema(operation_description="partial_update description override", responses={404: 'slug not found'})
   def partial_update(self, request, *args, **kwargs):
      """partial_update method docstring"""
      ...

will override the description of the ``PATCH /article/{id}/`` operation, and document a 404 response with no body and
the given description.

Where you can use the :func:`@swagger_auto_schema <.swagger_auto_schema>` decorator depends on the type of your view:

* for function based ``@api_view``\ s, because the same view can handle multiple methods, and thus represent multiple
  operations, you have to add the decorator multiple times if you want to override different operations:

   .. code:: python

      test_param = openapi.Parameter('test', openapi.IN_QUERY, description="test manual param", type=openapi.TYPE_BOOLEAN)
      user_response = openapi.Response('response description', UserSerializer)

      @swagger_auto_schema(method='get', manual_parameters=[test_param], responses={200: user_response})
      @swagger_auto_schema(methods=['put', 'post'], request_body=UserSerializer)
      @api_view(['GET', 'PUT', 'POST'])
      def user_detail(request, pk):
          ...

* for class based ``APIView``, ``GenericAPIView`` and non-``ViewSet`` derivatives, you have to decorate the respective
  method of each operation:

   .. code:: python

      class UserList(APIView):
         @swagger_auto_schema(responses={200: UserSerializer(many=True)})
         def get(self, request):
            ...

         @swagger_auto_schema(operation_description="description")
         def post(self, request):
            ...

* for ``ViewSet``, ``GenericViewSet``, ``ModelViewSet``, because each viewset corresponds to multiple **paths**, you have
  to decorate the *action methods*, i.e. ``list``, ``create``, ``retrieve``, etc. |br|
  Additionally, ``@list_route``\ s or ``@detail_route``\ s defined on the viewset, like function based api views, can
  respond to multiple HTTP methods and thus have multiple operations that must be decorated separately:


   .. code:: python

      class ArticleViewSet(viewsets.ModelViewSet):
         @swagger_auto_schema(operation_description='GET /articles/today/')
         @list_route(methods=['get'])
         def today(self, request):
            ...

         @swagger_auto_schema(method='get', operation_description="GET /articles/{id}/image/")
         @swagger_auto_schema(method='post', operation_description="POST /articles/{id}/image/")
         @detail_route(methods=['get', 'post'], parser_classes=(MultiPartParser,))
         def image(self, request, id=None):
            ...

         @swagger_auto_schema(operation_description="PUT /articles/{id}/")
         def update(self, request, *args, **kwargs):
            ...

         @swagger_auto_schema(operation_description="PATCH /articles/{id}/")
         def partial_update(self, request, *args, **kwargs):
            ...


*************************
Subclassing and extending
*************************

For more advanced control you can subclass :class:`.SwaggerAutoSchema` - see the documentation page for a list of
methods you can override.

You can put your custom subclass to use by setting it on a view method using the
:func:`@swagger_auto_schema <.swagger_auto_schema>` decorator described above.

If you need to control things at a higher level than :class:`.Operation` objects (e.g. overall document structure,
vendor extensions in metadata) you can also subclass :class:`.OpenAPISchemaGenerator` - again, see the documentation
page for a list of its methods.

This custom generator can be put to use by setting it as the :attr:`.generator_class` of a :class:`.SchemaView` using
:func:`.get_schema_view`.
