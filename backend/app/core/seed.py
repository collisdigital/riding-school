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
    ("riders:edit", "Edit existing riders"),
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

    db.flush() # Ensure IDs are generated

    # 3. Assign Permissions to Roles
    all_perms = list(perms_map.values())

    for role_name, mapping in ROLE_PERMISSIONS.items():
        role = roles_map.get(role_name)
        if not role:
            # Should be created in step 1, but safe check
            continue

        target_perms = []
        if mapping == "all":
            target_perms = all_perms
        else:
            target_perms = [perms_map[p] for p in mapping if p in perms_map]

        # Update role permissions
        # We can clear and re-add, or append unique.
        # Since this is seed, ensuring they are present is key.
        # Simple way: role.permissions = target_perms
        # This will update the association table.

        # Check if we should overwrite existing custom assignments?
        # For seed, enforcing default structure is usually desired.
        role.permissions = target_perms

    db.commit()
