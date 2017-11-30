# drf-swagger - Yet another Swagger generator for Django Rest Framework

_**WARNING**: this project is under rapid development; the APIs described here might change at any time without notice_

## Background

`OpenAPI 2.0`, 'formerly known as' `Swagger`, is a format designed to encode information about a Web API into an 
easily parsable schema that can then be used for rendering documentation, generating code, etc. 

More details are available on [swagger.io](https://swagger.io/) and on the 
[OpenAPI 2.0 specification page](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md).

From here on, the terms "OpenAPI" and "Swagger" are used interchangeably.

#### Swagger in Django Rest Framework

Since Django Rest 3.7, there is now [built in support](http://www.django-rest-framework.org/api-guide/schemas/) for 
automatic OpenAPI (Swagger) 2.0 schema generation. However, this generation is based on the 
[coreapi](http://www.coreapi.org/) standard, which for the moment is vastly inferior to OpenAPI in both support and 
features. In particular, the OpenAPI codec/compatibility layer provided has a few major problems:
* there is no support for documenting response schemas and status codes
* nested schemas do not work properly
* does not handle more complex fields such as `FileField`, `ChoiceField`, ...

In short this makes the generated schema unusable for code generation, and mediocre at best for documentation.

#### Third-party libraries
There  are currently two decent Swagger schema generators that I could find for django-rest-framework:
* [django-rest-swagger](https://github.com/marcgibbons/django-rest-swagger)
* [drf-openapi](https://github.com/limdauto/drf_openapi)

Out of the two, `django-rest-swagger` is just a wrapper around DRF 3.7 schema generation with an added UI, and thus has
the same problems. `drf-openapi` is a bit more involved and implements some custom handling for response schemas, but 
ultimately still falls short in code generation because the responses are plain `object`s.

Both projects are also relatively dead and stagnant.


## Table of contents

<!-- toc -->

- [Design](#design)
  * [Aim](#aim)
  * [Implementation progress](#implementation-progress)
    + [Features](#features)
- [Usage](#usage)
  * [1. Quickstart](#1-quickstart)
  * [2. Configuration](#2-configuration)
      - [a. `get_schema_view` parameters](#a-get_schema_view-parameters)
      - [b. `SchemaView` instantiators](#b-schemaview-instantiators)
      - [c. `SWAGGER_SETTINGS` and `REDOC_SETTINGS`](#c-swagger_settings-and-redoc_settings)
  * [3. More customization](#3-more-customization)
  * [4. Caching](#4-caching)
  * [5. Validation](#5-validation)
    + [`swagger-ui` validation badge](#swagger-ui-validation-badge)
      - [Online](#online)
      - [Offline](#offline)
    + [using `swagger-cli`](#using-swagger-cli)
    + [manually, on `editor.swagger.io`](#manually-on-editorswaggerio)
- [Planned feature support](#planned-feature-support)

<!-- tocstop -->

## Design

### Aim
This project aims for full compatibility with Swagger/OpenAPI 2.0 code generation tools. More precisely, this means:
* support documentation of response schemas for multiple possible status codes
* support unbounded schema nesting
* generate real OpenAPI Schema definitions instead of inline models
* allow easy and pluggable manual overrides for all schema components

### Implementation progress

For the first release, most of `django-rest-swagger`'s functionality is implemented. A lot of inspiration and code was 
drawn from the existing implementations mentioned above, so thanks are due to their respective authors. 

#### Features
* schema generation is a wrapper around coreapi & drf
* bundled latest version of [swagger-ui](https://github.com/swagger-api/swagger-ui) and 
  [redoc](https://github.com/Rebilly/ReDoc)
* supports dumping of schema in JSON and YAML
* schema view is cacheable out of the box
* generated Swagger schema can be automatically validated by [flex](https://github.com/pipermerriam/flex) or 
  [swagger-spec-validator](https://github.com/Yelp/swagger_spec_validator)


![Swagger UI](/screenshots/snippets-swagger-ui.png?raw=true "Snippets API in Swagger UI")
![ReDoc](/screenshots/snippets-redoc.png?raw=true "Snippets API in ReDoc")


## Usage

### 1. Quickstart
In `settings.py`:
```python

INSTALLED_APPS = [
    ...
    'drf_swagger',
    ...
]
```

In `urls.py`:
```python
...
from drf_swagger.views import get_schema_view
from drf_swagger import openapi

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
    validators=['flex', 'ssv'],
    public=False,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    url(r'^swagger(?P<format>.json|.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
    ...
]
```

You've just created:
* A JSON view of your schema at `/swagger.json`
* A YAML view of your schema at `/swagger.yaml`
* A swagger-ui view of your schema at `/swagger/`
* A ReDoc view of your schema at `/redoc/`

### 2. Configuration
##### a. `get_schema_view` parameters
* `info` - Required. Swagger API Info object
* `url` - API base url; if left blank will be deduced from the location the view is served at
* `patterns` - passed to SchemaGenerator
* `urlconf` - passed to SchemaGenerator
* `public` - if False, includes only endpoints the current user has access to
* `validators` - a list of validator names to apply on the generated schema; allowed values are `flex`, `ssv`
* `authentication_classes` - authentication classes for the schema view itself
* `permission_classes` - permission classes for the schema view itself

##### b. `SchemaView` instantiators
* `SchemaView.with_ui(renderer, ...)` - get a view instance using the specified UI renderer; one of `swagger`, `redoc`
* `SchemaView.without_ui(...)` - get a view instance with no UI renderer; same as `as_cached_view` with no kwargs
* `SchemaView.as_cached_view(...)` - same as `as_view`, but with optional caching
* you can, of course, call `as_view` as usual

All of the first 3 methods take two optional arguments, `cache_timeout` and `cache_kwargs`; if present, these are
passed on to Django's `cached_page` decorator in order to enable caching on the resulting viewl. 
See [4. Caching](#4-caching).


##### c. `SWAGGER_SETTINGS` and `REDOC_SETTINGS`
Additionally, you can include some more settings in your `settings.py` file. 
The possible settings and their default values are as follows:

```python
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
    
    # swagger-ui configuration settings, see https://github.com/swagger-api/swagger-ui#parameters of the same name
    'OPERATIONS_SORTER': None,
    'TAGS_SORTER': None,
    'DOC_EXPANSION': 'list',
    'DEEP_LINKING': False,
    'SHOW_EXTENSIONS': True,
    'DEFAULT_MODEL_RENDERING': 'model',
    'DEFAULT_MODEL_DEPTH': 2,
}
```

```python
REDOC_SETTINGS = {
    # ReDoc UI configuration settings, see https://github.com/Rebilly/ReDoc#redoc-tag-attributes
    'LAZY_RENDERING': True,
    'HIDE_HOSTNAME': False,
    'EXPAND_RESPONSES': 'all',
    'PATH_IN_MIDDLE': False,
}
```

### 3. More customization
Should you have need of more fine-grained customization over the schema view and generation, you are on your own to 
figure out where you need to subclass and plug your functionality. Here are a few high-level hints:

* `OpenAPISchemaGenerator` enumerates all the API endpoints registered in Django Rest Framework, inspects their view 
  classes and generates an appropriate `Swagger` object describing the API structure
* `SchemaView` gets a `drf_swagger.openapi.Swagger` schema object from a generator and renders it into an HTTP response
  * you can subclass `SchemaView` by extending the return value of `get_schema_view`, e.g.:
    ```python
    SchemaView = get_schema_view(info, ...)
    
    class CustomSchemaView(SchemaView):
        generator_class = CustomSchemaGenerator
        renderer_classes = (CustomRenderer1, CustomRenderer2,)
    ```

* `drf_swagger.renderers` take a `Swagger` object and transform it into an OpenAPI 2.0 specification document
 using `OpenAPICodecJson`, `OpenAPICodecYaml`, or into a web interface using an OpenAPI renderer library.
* `drf_swagger.codecs` take a `Swagger` object and encode it in an exportable format (json or yaml by default).

### 4. Caching
Since the schema does not usually change during the lifetime of the django process, there is out of the box support 
for caching the schema view in-memory, with some sane defaults:
* caching is enabled by the [`cache_page`](https://docs.djangoproject.com/en/1.11/topics/cache/#the-per-view-cache) 
decorator,  using the default Django cache backend but this can be changed using the `cache_kwargs` argument
* HTTP caching of the response is blocked to avoid confusing situations caused by being served stale schemas
* the cached schema varies on the `Cookie` and `Authorization` HTTP headers to enable filtering of visible endpoints 
  according to the authentication credentials of each user; note that this means that every user accessing the schema
  will have a separate schema cached in memory.
  
### 5. Validation
Given the numerous methods to manually customzie the generated schema, it makes sense to validate the result to ensure
it still conforms to OpenAPI 2.0. To this end, validation is provided at the generation point using python swagger
libraries, and can be activated by passing `validators=['flex', 'ssv']` to get_schema_view; if the generated schema
is not valid, a `SwaggerValidationError` is raised by the handling codec and nothing is returned.

**Warning:** This internal validation is quite slow and can be a DOS vector if left activated on a publicly available view. 

Caching can mitigate the speed impact of validation on restricted views.

The provided validation will catch syntactic errors, but more subtle violations of the spec might slip by them. To
ensure compatibility with code generation tools, it is recommended to also employ one or more of the following methods:
- #### `swagger-ui` validation badge

    ##### Online
    If your schema is publicly accessible, `swagger-ui` will automatically validate it against the official swagger 
    online validator and display the result in the bottom-right validation badge.
    ##### Offline
    If your schema is not accessible from the internet, you can run a local copy of 
    [swagger-validator](https://hub.docker.com/r/swaggerapi/swagger-validator/) and set the `VALIDATOR_URL` accordingly:
    ```python
    SWAGGER_SETTINGS = {
        ...
        'VALIDATOR_URL': 'http://localhost:8189',
        ...
    }
    ```
    
    ```bash
    $ docker run --name swagger-validator -d -p 8189:8080 --add-host test.local:10.0.75.1 swaggerapi/swagger-validator
    84dabd52ba967c32ae6b660934fa6a429ca6bc9e594d56e822a858b57039c8a2
    $ curl http://localhost:8189/debug?url=http://test.local:8002/swagger/?format=openapi
    {}
    ```
    
- #### using `swagger-cli`
    [https://www.npmjs.com/package/swagger-cli](https://www.npmjs.com/package/swagger-cli)
    ```bash
    $ npm install -g swagger-cli
    [...]
    $ swagger-cli validate http://test.local:8002/swagger.yaml
    http://test.local:8002/swagger.yaml is valid
    ```
    
- #### manually, on `editor.swagger.io`
    Importing the generated spec into [https://editor.swagger.io/](https://editor.swagger.io/) will automatically 
    trigger validation on it.


## Planned feature support
* **OpenAPI 3.0** - if I get 2.0 working like I want, and it's not too hard to adapt to 3.0