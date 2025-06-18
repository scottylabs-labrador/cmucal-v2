from app.models.models import Admin
from typing import List

def create_admin(db, org_id: int, user_id: int, role: str = "admin", category_id: int = None):
    """
    Create a new admin in the database.

    Args:
        db: Database session.
        org_id: ID of the organization.
        user_id: ID of the user.

    Returns:
        The created Admin object.
    """
    admin = Admin(org_id=org_id, user_id=user_id, role=role, category_id=category_id)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

def get_admin_by_org_and_user(db, org_id: int, user_id: int):
    """
    Retrieve an admin by organization ID and user ID.
    Args:
        db: Database session.
        org_id: ID of the organization.
        user_id: ID of the user.
    Returns:
        The Admin object if found, otherwise None.
    """
    return db.query(Admin).filter(
        Admin.org_id == org_id,
        Admin.user_id == user_id
    ).first()

def delete_admin(db, org_id: int, user_id: int):
    """
    Delete an admin by organization ID and user ID.
    Args:
        db: Database session.
        org_id: ID of the organization.
        user_id: ID of the user.
    Returns:
        True if the admin was deleted, False if it was not found.
    """
    admin = db.query(Admin).filter(
        Admin.org_id == org_id,
        Admin.user_id == user_id
    ).first()
    
    if admin:
        db.delete(admin)
        db.commit()
        return True
    return False

def get_admins_by_org(db, org_id: int):
    """
    Retrieve all admins for a given organization.
    Args:
        db: Database session.
        org_id: ID of the organization.
    Returns:
        A list of Admin objects for the organization.
    """
    return db.query(Admin).filter(Admin.org_id == org_id).all()

def get_admins_by_user(db, user_id: int):
    """
    Retrieve all organizations where the user is an admin.
    Args:
        db: Database session.
        user_id: ID of the user.
    Returns:
        A list of Admin objects where the user is an admin.
    """
    return db.query(Admin).filter(Admin.user_id == user_id).all()

def get_admins_by_orgs(db, org_ids: List[int]):
    """
    Retrieve all admins for a list of organization IDs.
    Args:
        db: Database session.
        org_ids: List of organization IDs.
    Returns:    
        A list of Admin objects for the specified organizations.
    """
    return db.query(Admin).filter(Admin.org_id.in_(org_ids)).all()