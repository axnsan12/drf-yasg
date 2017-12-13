from drf_yasg import openapi


def test_operation_docstrings(swagger_dict):
    users_list = swagger_dict['paths']['/users/']
    assert users_list['get']['description'] == "UserList cbv classdoc"
    assert users_list['post']['description'] == "apiview post description override"

    users_detail = swagger_dict['paths']['/users/{id}/']
    assert users_detail['get']['description'] == "user_detail fbv docstring"
    assert users_detail['put']['description'] == "user_detail fbv docstring"


def test_parameter_docstrings(swagger_dict):
    users_detail = swagger_dict['paths']['/users/{id}/']
    assert users_detail['get']['parameters'][0]['description'] == "test manual param"
    assert users_detail['put']['parameters'][0]['in'] == openapi.IN_BODY
