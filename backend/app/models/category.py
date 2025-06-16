from app.models.models import Category 

def create_category(db, org_id: int, name: str):
    """
    Create a new category in the database.

    Args:
        db: Database session.
        org_id: ID of the organization.
        name: Name of the category.
        description: Description of the category (optional).

    Returns:
        The created Category object.
    """
    category = Category(org_id=org_id, name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return f"Category {category.id} created"

def get_category_by_id(db, category_id: int):
    """
    Retrieve a category by its ID.

    Args:
        db: Database session.
        category_id: ID of the category.

    Returns:
        The Category object if found, otherwise None.
    """
    return db.query(Category).filter(Category.id == category_id).first()
def delete_category(db, category_id: int):
    """
    Delete a category by its ID.
    Args:
        db: Database session.
        category_id: ID of the category to delete.
    Returns:
        True if the category was deleted, False if it was not found.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if category:
        db.delete(category)
        db.commit()
        return True
    return False
def get_categories_by_org(db, org_id: int):
    """
    Retrieve all categories for a given organization.
    Args:
        db: Database session.
        org_id: ID of the organization.
    Returns:
        A list of Category objects.
    """
    return db.query(Category).filter(Category.org_id == org_id).all()