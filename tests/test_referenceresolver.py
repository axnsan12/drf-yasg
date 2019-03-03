import pytest

from drf_yasg.openapi import ReferenceResolver


def test_basic():
    scopes = ['s1', 's2']
    rr = ReferenceResolver(*scopes, force_init=True)
    assert scopes == rr.scopes == list(rr.keys()) == list(rr)
    rr.set('o1', 1, scope='s1')
    assert rr.has('o1', scope='s1')
    assert rr.get('o1', scope='s1') == 1

    rr.setdefault('o1', lambda: 2, scope='s1')
    assert rr.get('o1', scope='s1') == 1
    assert not rr.has('o1', scope='s2')

    rr.setdefault('o3', lambda: 3, scope='s2')
    assert rr.get('o3', scope='s2') == 3

    assert rr['s1'] == {'o1': 1}
    assert dict(rr) == {'s1': {'o1': 1}, 's2': {'o3': 3}}
    assert str(rr) == str(dict(rr))


def test_scoped():
    scopes = ['s1', 's2']
    rr = ReferenceResolver(*scopes, force_init=True)
    r1 = rr.with_scope('s1')
    r2 = rr.with_scope('s2')
    with pytest.raises(AssertionError):
        rr.with_scope('bad')

    assert r1.scopes == ['s1']
    assert list(r1.keys()) == list(r1) == []

    r2.set('o2', 2)
    assert r2.scopes == ['s2']
    assert list(r2.keys()) == list(r2) == ['o2']
    assert r2['o2'] == 2

    with pytest.raises(AssertionError):
        r2.get('o2', scope='s1')

    assert rr.get('o2', scope='s2') == 2
