from app.models.models import Admin, Category
from typing import List
from sqlalchemy.orm import aliased
from sqlalchemy import or_

def admin_to_dict(admin):
    return {
        "user_id": admin.user_id,
        "org_id": admin.org_id,
        "category_id": admin.category_id if admin.category_id else None,
        "role": admin.role,
        "created_at": admin.created_at.isoformat() if admin.created_at else None,
    }

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

def get_categories_for_admin_user(db, user_id: int):
    """
    Retrieve all categories where the user is an admin or manager.
    
    - 'manager': access to all categories in the org
    - 'admin': access to the specific category_id
    
    Args:
        db: Database session
        user_id: ID of the user
    
    Returns:
        A list of Category objects
    """
    # Get all relevant admin entries
    admin_entries = db.query(Admin).filter(
        Admin.user_id == user_id,
        Admin.role.in_(["admin", "manager"])
    ).all()

    # Collect category IDs
    category_ids = set()

    for admin in admin_entries:
        if admin.role == "manager":
            # Add all categories in the org
            org_category_ids = db.query(Category.id).filter(Category.org_id == admin.org_id).all()
            category_ids.update(cid for (cid,) in org_category_ids)
        elif admin.role == "admin" and admin.category_id is not None:
            category_ids.add(admin.category_id)

    categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
    return categories
    # Remove potential duplicates (if any)
    # unique_categories = {category.id: category for category in categories}.values()
    # return list(unique_categories)
