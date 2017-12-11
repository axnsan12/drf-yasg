##################
Serving the schema
##################

********************************
The ``get_schema_view`` function
********************************

************************
The ``SchemaView`` class
************************

``SchemaView`` gets a ``drf_swagger.openapi.Swagger`` schema object
from a generator and renders it into an HTTP response

   you can subclass ``SchemaView`` by extending the return value of ``get_schema_view``, e.g.:

   .. code:: python

       SchemaView = get_schema_view(info, ...)

       class CustomSchemaView(SchemaView):
           generator_class = CustomSchemaGenerator
           renderer_classes = (CustomRenderer1, CustomRenderer2,)

********************
Renderers and codecs
********************

-  ``drf_swagger.renderers`` take a ``Swagger`` object and render it into an HTTP response;
   renderers for JSON, YAML and HTML web UI are provided by default
-  ``drf_swagger.codecs`` take a ``Swagger`` object and encode it into a text format (json or yaml by default).
