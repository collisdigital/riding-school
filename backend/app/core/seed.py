from sqlalchemy.orm import Session

from app.models.permission import Permission
from app.models.role import Role

ROLES = [
    (Role.ADMIN, "Administrator"),
    (Role.INSTRUCTOR, "Instructor"),
    (Role.PARENT, "Parent"),
    (Role.RIDER, "Student Rider"),
]

PERMISSIONS = [
    # Rider Management
    ("riders:create", "Create new riders"),
    ("riders:update", "Edit existing riders"),
    ("riders:delete", "Delete riders"),
    ("riders:view", "View riders"),
    # Progression
    ("grades:signoff", "Sign off rider grades"),
    ("grades:view_history", "View rider progression history"),
    # School Admin
    ("staff:invite", "Invite new staff"),
    ("staff:manage_roles", "Manage staff roles"),
    ("school:edit_settings", "Edit school settings"),
]

ROLE_PERMISSIONS = {
    Role.ADMIN: "all",
    Role.INSTRUCTOR: ["riders:view", "grades:signoff", "grades:view_history"],
    Role.PARENT: ["riders:view", "grades:view_history"],
    # RIDER: [],
}


def seed_rbac(db: Session):
    # 1. Ensure Roles exist
    roles_map = {}
    for name, desc in ROLES:
        role = db.query(Role).filter(Role.name == name).first()
        if not role:
            role = Role(name=name, description=desc)
            db.add(role)
        roles_map[name] = role

    # 2. Ensure Permissions exist
    perms_map = {}
    for name, desc in PERMISSIONS:
        perm = db.query(Permission).filter(Permission.name == name).first()
        if not perm:
            perm = Permission(name=name, description=desc)
            db.add(perm)
        perms_map[name] = perm

    db.flush()  # Ensure IDs are generated

    # 3. Assign Permissions to Roles (Additive / Initial only)
    all_perms = list(perms_map.values())

    for role_name, mapping in ROLE_PERMISSIONS.items():
        role = roles_map.get(role_name)
        if not role:
            continue

        # Check if role already has ANY permissions assigned
        # If so, assume it's been customized or already seeded, and do NOT overwrite.
        if role.permissions:
            continue

        target_perms = []
        if mapping == "all":
            target_perms = all_perms
        else:
            target_perms = [perms_map[p] for p in mapping if p in perms_map]

        # Apply default permissions since none exist
        role.permissions = target_perms

    db.commit()
