def test_paths_not_empty(swagger_dict):
    assert len(swagger_dict['paths']) > 0
