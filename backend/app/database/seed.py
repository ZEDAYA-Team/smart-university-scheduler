"""Small, opt-in development seed used by docker-compose only."""
from sqlalchemy.orm import Session
from app.database.base import SessionLocal
from app.models.auth import Role, User
from app.security import hash_password

DEMO_USERS = [("departmenthead@sutms.local", "Department", "User", "department_head"), ("admin@sutms.local", "Admin", "User", "admin"), ("lecturer@sutms.local", "Lecturer", "User", "lecturer"), ("student@sutms.local", "Student", "User", "student")]

def seed_development_data() -> None:
    db: Session = SessionLocal()
    try:
        for role_name in ("admin", "lecturer", "student", "department_head"):
            if db.query(Role).filter_by(name=role_name).first() is None:
                db.add(Role(name=role_name))
        db.flush()
        for email, first_name, last_name, role_name in DEMO_USERS:
            if db.query(User).filter_by(email=email).first() is None:
                role = db.query(Role).filter_by(name=role_name).one()
                db.add(User(email=email, first_name=first_name, last_name=last_name, role_id=role.role_id, password_hash=hash_password("ChangeMe123!")))
        db.commit()
    finally:
        db.close()
