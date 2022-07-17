from collections import OrderedDict
from random import shuffle

from drf_yasg import openapi


def test_vendor_extensions():
    """Any attribute starting with x_ should map to a vendor property of the form x-camelCase"""
    sd = openapi.SwaggerDict(x_vendor_ext_1='test')
    sd.x_vendor_ext_2 = 'test'
    assert 'x-vendorExt1' in sd
    assert sd.x_vendor_ext_1 == 'test'
    assert sd['x-vendorExt2'] == 'test'

    del sd.x_vendor_ext_1
    assert 'x-vendorExt1' not in sd


def test_ref():
    """The attribute 'ref' maps to the swagger key '$ref'"""
    sd = openapi.SwaggerDict(ref='reftest')
    assert '$ref' in sd
    assert sd['$ref'] == sd.ref == 'reftest'

    del sd['$ref']
    assert not hasattr(sd, 'ref')


def test_leading_underscore_ignored():
    """Attributes with a leading underscore are set on the object as-is and are not added to its dict form"""
    sd = openapi.SwaggerDict(_private_attr_1='not_camelized')
    initial_len = len(sd)
    sd._nope = 'not camelized either'
    assert len(sd) == initial_len
    assert 'privateAttr1' not in sd
    assert sd._private_attr_1 == 'not_camelized'
    assert '_private_attr_1' not in sd
    assert hasattr(sd, '_nope')

    del sd._nope
    assert not hasattr(sd, '_nope')


def test_trailing_underscore_stripped():
    """Trailing underscores are stripped when converting attribute names.
    This allows, for example, python keywords to function as SwaggerDict attributes."""
    sd = openapi.SwaggerDict(trailing_underscore_='trailing')
    sd.in_ = 'trailing'
    assert 'in' in sd
    assert 'trailingUnderscore' in sd
    assert sd.trailing_underscore == sd['in']
    assert hasattr(sd, 'in___')

    del sd.in_
    assert 'in' not in sd
    assert not hasattr(sd, 'in__')


def test_extra_ordering():
    """Insertion order should also be consistent when setting undeclared parameters (kwargs) in SwaggerDict"""
    extras = [('beta', 1), ('alpha', 2), ('omega', 3), ('gamma', 4)]
    shuffled_extras = list(extras)
    shuffle(shuffled_extras)

    s1 = openapi.SwaggerDict(**OrderedDict(extras))
    s2 = openapi.SwaggerDict(**OrderedDict(shuffled_extras))

    assert list(s1.items()) == list(s2.items())
