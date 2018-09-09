######################
Customizing the web UI
######################

The web UI can be customized using the settings available in :ref:`swagger-ui-settings` and :ref:`redoc-ui-settings`.

You can also extend one of the ``drf-yasg/swagger-ui.html`` or ``drf-yasg/redoc.html`` templates that are used for
rendering. The customizable blocks are currently limited to:

{% block extra_styles %}
  additional stylesheets

{% block extra_scripts %}
  additional scripts

{% block user_context_message %}
  *(swagger-ui session auth only)*
  logged in user message
