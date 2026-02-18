import uuid

from app.models.role import Role


def test_role_get_id_populates_cache_only_after_commit(db_session):
    role_id = Role.get_id(db_session, Role.ADMIN)
    assert role_id is not None
    assert Role.get_cached_id(Role.ADMIN) is None

    db_session.commit()

    assert Role.get_cached_id(Role.ADMIN) == role_id


def test_role_cache_stages_new_role_until_commit(db_session):
    role_name = f"CACHE_ROLE_{uuid.uuid4().hex[:8]}"
    role = Role(name=role_name, description="Staged cache role")
    db_session.add(role)
    db_session.flush()

    Role.stage_cache_update(db_session, role_name, role.id)
    assert Role.get_cached_id(role_name) is None

    db_session.commit()

    assert Role.get_cached_id(role_name) == role.id


def test_role_cache_discards_staged_entries_on_rollback(db_session):
    role_name = f"ROLLED_BACK_ROLE_{uuid.uuid4().hex[:8]}"
    role = Role(name=role_name, description="Rollback cache role")
    db_session.add(role)
    db_session.flush()

    Role.stage_cache_update(db_session, role_name, role.id)
    assert Role.get_cached_id(role_name) is None

    db_session.rollback()

    assert Role.get_cached_id(role_name) is None
    assert db_session.query(Role).filter(Role.name == role_name).first() is None
