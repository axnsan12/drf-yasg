# DRF - Yet another Swagger generator 2

Automated generation of real Swagger/OpenAPI 2.0 schemas from Django REST
Framework code.

## Status

| Source     | Shields                                                        |
| ---------- | -------------------------------------------------------------- |
| Project    | ![release][release] ![build][build]        |
| Publishers | [![pypi][pypi]][pypi_link]                                     |
| Downloads  | ![pypi_downloads][pypi_downloads]                              |
| Raised     | [![issues][issues]][issues_link] [![pulls][pulls]][pulls_link] |

## Compatibility

| Release | Python     | Django    | Django REST Framework |
|:-------:|:----------:|:---------:|:---------------------:|
| 1.18.x  | 2.7        | 1.11      | 3.8 - 3.9             |
| 1.18.x  | 3.6 - 3.8  | 2.2 - 3.0 | 3.8 - 3.12            |
| 1.19.x  | 3.6 - 3.9  | 2.2 - 3.0 | 3.8 - 3.12            |

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

Additionally, if you want to use the built-in validation mechanisms
you need to install some extra requirements:

```bash
pip install drf-yasg2[validation]
```

### Usage

Checkout the [live demo!](https://drf_yasg2-demo.herokuapp.com/)

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
      url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
      url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
      url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
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

* **Cristi Vîjdea** - _Initial work_ - [Joel Lefkowitz](https://github.com/axnsan12)

* **Joel Lefkowitz** - _This fork's maintainer_ - [Joel Lefkowitz](https://github.com/JoelLefkowitz)

Huge thank you to the contributors who've participated in this project. Have a look at the [contributions](https://github.com/JoelLefkowitz/drf-yasg/pulse)!

### License

This project is licensed under the BSD 3-Clause License - see the [LICENSE.md](LICENSE.md) file for details

<!--- Table links --->

[release]: https://img.shields.io/github/v/tag/joellefkowitz/drf-yasg
[build]:  https://travis-ci.org/JoelLefkowitz/drf-yasg.svg?branch=master

[pypi_downloads]: https://img.shields.io/pypi/dw/drf_yasg2

[pypi]: https://img.shields.io/pypi/v/drf_yasg2 "PyPi"
[pypi_link]: https://pypi.org/project/drf_yasg2

[issues]: https://img.shields.io/github/issues/JoelLefkowitz/drf-yasg "Issues"
[issues_link]: https://github.com/JoelLefkowitz/drf-yasg/issues

[pulls]: https://img.shields.io/github/issues-pr/JoelLefkowitz/drf-yasg "Pull requests"
[pulls_link]: https://github.com/JoelLefkowitz/drf-yasg/pulls

<!--- Image links --->

[redoc_screenshot]: https://raw.githubusercontent.com/JoelLefkowitz/drf-yasg/1.0.2/screenshots/redoc-nested-response.png

[swagger_ui_screenshot]: https://raw.githubusercontent.com/JoelLefkowitz/drf-yasg/1.0.2/screenshots/swagger-ui-list.png

[models_screenshot]: https://raw.githubusercontent.com/JoelLefkowitz/drf-yasg/1.0.2/screenshots/swagger-ui-models.png
