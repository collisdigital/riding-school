from sqlalchemy.orm import Session

from app.models.role import Role

ROLES = [
    (Role.ADMIN, "Administrator"),
    (Role.INSTRUCTOR, "Instructor"),
    (Role.PARENT, "Parent"),
    (Role.RIDER, "Student Rider"),
]


def seed_rbac(db: Session):
    for name, desc in ROLES:
        role = db.query(Role).filter(Role.name == name).first()
        if not role:
            role = Role(name=name, description=desc)
            db.add(role)

    db.commit()
