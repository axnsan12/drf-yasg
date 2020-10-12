######################
Customizing the web UI
######################

The web UI can be customized using the settings available in :ref:`swagger-ui-settings` and :ref:`redoc-ui-settings`.

You can also extend one of the `drf_yasg2/swagger-ui.html`_ or `drf_yasg2/redoc.html`_ templates that are used for
rendering. See the template source code (linked above) for a complete list of customizable blocks.

The ``swagger-ui`` view has some quite involed JavaScript hooks used for some functionality, which you might also
want to review at `drf_yasg2/swagger-ui-init.js`_.

.. _drf_yasg2/swagger-ui.html: https://github.com/joellefkowitz/drf-yasg/blob/master/src/drf_yasg/templates/drf_yasg2/swagger-ui.html
.. _drf_yasg2/swagger-ui-init.js: https://github.com/joellefkowitz/drf-yasg/blob/master/src/drf_yasg/static/drf_yasg2/swagger-ui-init.js
.. _drf_yasg2/redoc.html: https://github.com/joellefkowitz/drf-yasg/blob/master/src/drf_yasg/templates/drf_yasg2/redoc.html
