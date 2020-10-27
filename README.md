# DRF - Yet another Swagger generator 2

Automated generation of real Swagger/OpenAPI 2.0 schemas from Django REST
Framework code.

## Notice

The original [drf-yasg](https://github.com/joellefkowitz/drf-yasg) repository is now maintained again. This repo will be left as is to serve those still using it.

Please migrate back to the using the origional repository and for submitting contributions.

## Status

| Source     | Shields                                                           |
| ---------- | ----------------------------------------------------------------- |
| Project    | [![release][release]][release_link] [![build][build]][build_link] |
| Publishers | [![pypi][pypi]][pypi_link]                                        |
| Downloads  | [![pypi_downloads][pypi_downloads]][pypi_downloads_link]          |
| Raised     | [![issues][issues]][issues_link] [![pulls][pulls]][pulls_link]    |

## Compatibility

| Release | Python     | Django    | Django REST Framework |
|:-------:|:----------:|:---------:|:---------------------:|
| 1.18.x  | 2.7        | 1.11      | 3.8 - 3.9             |
| 1.18.x  | 3.6 - 3.8  | 2.2 - 3.0 | 3.8 - 3.12            |
| 1.19.x  | 3.6 - 3.9  | 2.2 - 3.1 | 3.8 - 3.12            |

## Features

* Full support for nested Serializers and Schemas
* Response schemas and descriptions
* Model definitions compatible with codegen tools
* Customization hooks at all points in the spec generation process
* JSON and YAML format for spec
* Bundles latest version of [swagger-ui](https://github.com/swagger-api/swagger-ui)
and [redoc](https://github.com/Rebilly/ReDoc) for viewing the generated documentation

* Schema view is cacheable out of the box
* Generated Swagger schema can be automatically validated by [swagger-spec-validator](https://github.com/Yelp/swagger_spec_validator)

* Supports Django REST Framework API versioning with ``URLPathVersioning`` and
``NamespaceVersioning``; other DRF or custom versioning schemes are not currently
supported

### Screenshots

#### Fully nested request and response schemas

![Redoc screenshot][redoc_screenshot]
#### Choose between redoc and swagger-ui

![Swagger-ui screenshot][swagger_ui_screenshot]

#### Model definitions

![Models screenshot][models_screenshot]

### Installing

Installing the package from pypi:

```bash
pip install drf-yasg2
```

Given the numerous methods to manually customize the generated schema, it makes sense to validate the result to ensure it still conforms to OpenAPI 2.0. To this end, validation is provided at the generation point using Python Swagger libraries, and can be activated by passing `validators=['ssv']` to `get_schema_view`; if the generated schema is not valid, a `SwaggerValidationError` is raised by the handling codec. 

To provide the built-in validation mechanisms you can install the extra requirements:

```bash
pip install drf-yasg2[validation]
```

### Usage

Checkout the [live demo!](https://drf-yasg2.herokuapp.com/)

Add the package to INSTALLED_APPS:

```python

   INSTALLED_APPS = [
      ...
      'drf_yasg2',
      ...
   ]
```

Add the endpoints to urlpatterns:

```python
   
   from django.urls import path, re_path
   from rest_framework import permissions
   from drf_yasg2.views import get_schema_view
   from drf_yasg2 import openapi

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
      public=True,
      permission_classes=(permissions.AllowAny,),
   )

   urlpatterns = [
      re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
      path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
      path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
      ...
   ]
```

This exposes 4 endpoints:

* A JSON view of your API specification at ``/swagger.json``
* A YAML view of your API specification at ``/swagger.yaml``
* A swagger-ui view of your API specification at ``/swagger/``
* A ReDoc view of your API specification at ``/redoc/``

### Docs

Additional details are available in the [full documentation](https://drf_yasg2.readthedocs.io/en/latest/) and the [changelog](https://drf_yasg2.readthedocs.io/en/stable/changelog.html).

To generate the documentation locally:

```bash
scripts/docs.sh
```

### Tests

To run tests:

```bash
tox
```

### Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.

### Versioning

[SemVer](http://semver.org/) is used for versioning. For a list of versions available, see the tags on this repository.

### Authors

This project forked from [drf-yasg](https://github.com/joellefkowitz/drf-yasg).
Credit is given to [Cristi Vîjdea](https://github.com/axnsan12) and the original contributors.

* **Cristi Vîjdea** - _Initial work_ - [Cristi Vîjdea](https://github.com/axnsan12)

* **Joel Lefkowitz** - _This fork's maintainer_ - [Joel Lefkowitz](https://github.com/JoelLefkowitz)

Huge thank you to the contributors who've participated in this project. Have a look at the [contributions](https://github.com/JoelLefkowitz/drf-yasg/pulse)!

### License

This project is licensed under the BSD 3-Clause License - see the [LICENSE.md](LICENSE.md) file for details

<!--- Table links --->

[release]: https://img.shields.io/github/v/tag/joellefkowitz/drf-yasg
[release_link]: https://github.com/JoelLefkowitz/drf-yasg/releases
[build]:  https://travis-ci.org/JoelLefkowitz/drf-yasg.svg?branch=master
[build_link]: https://travis-ci.com/github/JoelLefkowitz/drf-yasg

[pypi_downloads]: https://img.shields.io/pypi/dw/drf-yasg2
[pypi_downloads_link]: https://pypistats.org/packages/drf-yasg2

[pypi]: https://img.shields.io/pypi/v/drf-yasg2 "PyPi"
[pypi_link]: https://pypi.org/project/drf-yasg2

[issues]: https://img.shields.io/github/issues/JoelLefkowitz/drf-yasg "Issues"
[issues_link]: https://github.com/JoelLefkowitz/drf-yasg/issues

[pulls]: https://img.shields.io/github/issues-pr/JoelLefkowitz/drf-yasg "Pull requests"
[pulls_link]: https://github.com/JoelLefkowitz/drf-yasg/pulls

<!--- Image links --->

[redoc_screenshot]: https://raw.githubusercontent.com/JoelLefkowitz/drf-yasg/1.0.2/screenshots/redoc-nested-response.png

[swagger_ui_screenshot]: https://raw.githubusercontent.com/JoelLefkowitz/drf-yasg/1.0.2/screenshots/swagger-ui-list.png

[models_screenshot]: https://raw.githubusercontent.com/JoelLefkowitz/drf-yasg/1.0.2/screenshots/swagger-ui-models.png
