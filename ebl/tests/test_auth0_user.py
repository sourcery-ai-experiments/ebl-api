import pytest
from ebl.auth0 import Auth0User


def create_profile(profile):
    return lambda: profile


def create_empty_profile():
    return create_profile({})


def test_has_scope():
    scope = 'scope'
    user = Auth0User({'scope': scope}, create_empty_profile)

    assert user.has_scope(scope) is True
    assert user.has_scope('other:scope') is False


def test_profile():
    profile = {'name': 'john'}
    user = Auth0User({}, create_profile(profile))

    assert user.profile == profile


@pytest.mark.parametrize("profile,expected", [
    ({'https://ebabylon.org/eblName': 'John', 'name': 'john'}, 'John'),
    ({'name': 'john'}, 'john')

])
def test_ebl_name(profile, expected):
    user = Auth0User({}, create_profile(profile))

    assert user.ebl_name == expected


@pytest.mark.parametrize("scopes,folio_name,expected", [
    ('read:WGL-folios', 'WGL', True),
    ('write:WGL-folios', 'WGL', False),
    ('read:XXX-folios', 'WGL', False)
])
def test_can_read_folio(scopes, folio_name, expected):
    user = Auth0User({'scope': scopes}, create_empty_profile)

    assert user.can_read_folio(folio_name) == expected
