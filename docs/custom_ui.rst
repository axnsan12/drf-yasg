######################
Customizing the web UI
######################

The web UI can be customized using the settings available in :ref:`swagger-ui-settings` and :ref:`redoc-ui-settings`.

You can also extend one of the `drf-yasg/swagger-ui.html`_ or `drf-yasg/redoc.html`_ templates that are used for
rendering. See the template source code (linked above) for a complete list of customizable blocks.

The ``swagger-ui`` view has some quite involved JavaScript hooks used for some functionality, which you might also
want to review at `drf-yasg/swagger-ui-init.js`_.

.. _drf-yasg/swagger-ui.html: https://github.com/axnsan12/drf-yasg/blob/master/src/drf_yasg/templates/drf-yasg/swagger-ui.html
.. _drf-yasg/swagger-ui-init.js: https://github.com/axnsan12/drf-yasg/blob/master/src/drf_yasg/static/drf-yasg/swagger-ui-init.js
.. _drf-yasg/redoc.html: https://github.com/axnsan12/drf-yasg/blob/master/src/drf_yasg/templates/drf-yasg/redoc.html
