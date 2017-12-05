def test_operation_docstrings(swagger_dict):
    users_list = swagger_dict['paths']['/users/']
    assert users_list['get']['description'] == "UserList cbv classdoc"

    users_detail = swagger_dict['paths']['/users/{id}/']
    assert users_detail['get']['description'] == "user_detail fbv docstring"
