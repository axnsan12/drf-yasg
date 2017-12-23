from datadiff.tools import assert_equal


def test_reference_schema(swagger_dict, reference_schema):
    swagger_dict = dict(swagger_dict)
    reference_schema = dict(reference_schema)
    ignore = ['info', 'host', 'schemes', 'basePath', 'securityDefinitions']
    for attr in ignore:
        swagger_dict.pop(attr, None)
        reference_schema.pop(attr, None)

    # formatted better than pytest diff
    assert_equal(swagger_dict, reference_schema)
