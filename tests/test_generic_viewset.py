def test_appropriate_status_codes(swagger_dict):
    articles_list = swagger_dict['paths']['/articles/']
    assert '200' in articles_list['get']['responses']
    assert '201' in articles_list['post']['responses']

    articles_detail = swagger_dict['paths']['/articles/{slug}/']
    assert '200' in articles_detail['get']['responses']
    assert '200' in articles_detail['put']['responses']
    assert '200' in articles_detail['patch']['responses']
    assert '204' in articles_detail['delete']['responses']


def test_operation_docstrings(swagger_dict):
    articles_list = swagger_dict['paths']['/articles/']
    assert articles_list['get']['description'] == "ArticleViewSet class docstring"
    assert articles_list['post']['description'] == "ArticleViewSet class docstring"

    articles_detail = swagger_dict['paths']['/articles/{slug}/']
    assert articles_detail['get']['description'] == "retrieve class docstring"
    assert articles_detail['put']['description'] == "update method docstring"
    assert articles_detail['patch']['description'] == "ArticleViewSet class docstring"
    assert articles_detail['delete']['description'] == "destroy method docstring"

    articles_today = swagger_dict['paths']['/articles/today/']
    assert articles_today['get']['description'] == "ArticleViewSet class docstring"

    articles_image = swagger_dict['paths']['/articles/{slug}/image/']
    assert articles_image['get']['description'] == "image method docstring"
    assert articles_image['post']['description'] == "image method docstring"
