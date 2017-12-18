from collections import OrderedDict

from datadiff.tools import assert_equal

from drf_yasg.codecs import yaml_sane_dump


def test_reference_schema(swagger_dict, reference_schema):
    # formatted better than pytest diff
    swagger_dict = OrderedDict(swagger_dict)
    reference_schema = OrderedDict(reference_schema)
    ignore = ['info', 'host', 'schemes', 'basePath', 'securityDefinitions']
    for attr in ignore:
        swagger_dict.pop(attr, None)
        reference_schema.pop(attr, None)

    try:
        assert_equal(swagger_dict, reference_schema)
    except AssertionError as e:
        if str(e).isspace():
            # ordering difference, print diff between strings
            assert_equal(yaml_sane_dump(swagger_dict, binary=False), yaml_sane_dump(reference_schema, binary=False))
        else:
            raise
