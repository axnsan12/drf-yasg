########################
Custom schema generation
########################

.. contents::
   :depth: 2

*********************
Swagger spec overview
*********************



**************************************
The ``@swagger_auto_schema`` decorator
**************************************


*************************
Subclassing and extending
*************************

``OpenAPISchemaGenerator`` enumerates all the API endpoints registered in Django Rest Framework, inspects their
view classes and generates an appropriate ``Swagger`` object describing the API structure
