from sqlalchemy.orm import Session
from app.models.rbac import Role, Permission

PERMISSIONS = [
    ("riders:view", "View riders"),
    ("riders:edit", "Edit riders"),
    ("riders:delete", "Delete riders"),
    ("staff:manage", "Manage staff and permissions"),
    ("grades:signoff", "Sign off on rider grades"),
]

ROLES = {
    "Admin": ["riders:view", "riders:edit", "riders:delete", "staff:manage", "grades:signoff"],
    "Instructor": ["riders:view", "riders:edit", "grades:signoff"],
    "Parent": ["riders:view"],
    "Rider": ["riders:view"],
}

def seed_rbac(db: Session):
    # 1. Create Permissions
    perm_map = {}
    for name, desc in PERMISSIONS:
        perm = db.query(Permission).filter(Permission.name == name).first()
        if not perm:
            perm = Permission(name=name, description=desc)
            db.add(perm)
            db.flush()
        perm_map[name] = perm

    # 2. Create Roles and link Permissions
    for role_name, perms in ROLES.items():
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            role = Role(name=role_name)
            db.add(role)
            db.flush()
        
        # Sync permissions
        role.permissions = [perm_map[p] for p in perms]
    
    db.commit()
