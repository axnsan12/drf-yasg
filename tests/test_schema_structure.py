def test_paths_not_empty(swagger_dict):
    assert len(swagger_dict['paths']) > 0


def test_appropriate_status_codes(swagger_dict):
    snippets_list = swagger_dict['paths']['/snippets/']
    assert '200' in snippets_list['get']['responses']
    assert '201' in snippets_list['post']['responses']
    snippets_detail = swagger_dict['paths']['/snippets/{id}/']
    assert '200' in snippets_detail['get']['responses']
    assert '200' in snippets_detail['put']['responses']
    assert '200' in snippets_detail['patch']['responses']
    assert '204' in snippets_detail['delete']['responses']


def test_operation_docstrings(swagger_dict):
    snippets_list = swagger_dict['paths']['/snippets/']
    assert snippets_list['get']['description'] == "SnippetList classdoc"
    assert snippets_list['post']['description'] == "post method docstring"
    snippets_detail = swagger_dict['paths']['/snippets/{id}/']
    assert snippets_detail['get']['description'] == "SnippetDetail classdoc"
    assert snippets_detail['put']['description'] == "put class docstring"
    assert snippets_detail['patch']['description'] == "patch method docstring"
    assert snippets_detail['delete']['description'] == "delete method docstring"
