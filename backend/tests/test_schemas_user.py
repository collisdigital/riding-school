from app.schemas.user import UserWithSchool


def test_parse_roles_none():
    # Test with None input
    assert UserWithSchool.parse_roles(None) == []


def test_parse_roles_empty_list():
    # Test with empty list
    assert UserWithSchool.parse_roles([]) == []


def test_parse_roles_strings():
    # Test with list of strings
    roles = ["admin", "instructor"]
    assert UserWithSchool.parse_roles(roles) == ["admin", "instructor"]


def test_parse_roles_objects_with_name():
    # Test with objects having a 'name' attribute
    class RoleMock:
        def __init__(self, name):
            self.name = name

    roles = [RoleMock("admin"), RoleMock("rider")]
    assert UserWithSchool.parse_roles(roles) == ["admin", "rider"]


def test_parse_roles_mixed():
    # Test with mixed strings and objects with 'name'
    class RoleMock:
        def __init__(self, name):
            self.name = name

    roles = ["admin", RoleMock("instructor")]
    assert UserWithSchool.parse_roles(roles) == ["admin", "instructor"]


def test_parse_roles_objects_without_name():
    # Test with objects without a 'name' attribute
    class OtherMock:
        def __str__(self):
            return "other"

    roles = [OtherMock()]
    assert UserWithSchool.parse_roles(roles) == ["other"]
