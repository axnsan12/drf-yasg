def test_reference_schema(swagger_dict, reference_schema):
    assert_equal(swagger_dict['paths'], reference_schema['paths'])


def assert_equal(dict1, dict2):
    """Compare two dictionaries bit by bit to get more manageable diffs"""
    for key, val in dict1.items():
        if isinstance(val, dict):
            assert_equal(dict1[key], dict2[key])
        else:
            assert dict1[key] == dict2[key]
