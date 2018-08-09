import json

import pytest

from drf_yasg import renderers


def _check_swagger_setting(swagger, setting, expected):
    context = {}
    renderer = renderers.SwaggerUIRenderer()
    renderer.set_context(context, swagger)

    swagger_settings = json.loads(context['swagger_settings'])
    assert swagger_settings[setting] == expected


def _check_setting(swagger, setting, expected):
    context = {}
    renderer = renderers.SwaggerUIRenderer()
    renderer.set_context(context, swagger)
    assert context[setting] == expected


def test_validator_url(swagger_settings, swagger):
    swagger_settings['VALIDATOR_URL'] = None
    _check_swagger_setting(swagger, 'validatorUrl', None)

    swagger_settings['VALIDATOR_URL'] = 'http://not.none/'
    _check_swagger_setting(swagger, 'validatorUrl', 'http://not.none/')

    with pytest.raises(KeyError):
        swagger_settings['VALIDATOR_URL'] = ''
        _check_swagger_setting(swagger, 'validatorUrl', None)


@pytest.mark.urls('urlconfs.login_test_urls')
def test_login_logout(swagger_settings, swagger):
    swagger_settings['LOGIN_URL'] = 'login'
    _check_setting(swagger, 'LOGIN_URL', '/test/login')

    swagger_settings['LOGOUT_URL'] = 'logout'
    _check_setting(swagger, 'LOGOUT_URL', '/test/logout')

    with pytest.raises(KeyError):
        swagger_settings['LOGIN_URL'] = None
        _check_setting(swagger, 'LOGIN_URL', None)

    with pytest.raises(KeyError):
        swagger_settings['LOGOUT_URL'] = None
        _check_setting(swagger, 'LOGOUT_URL', None)
