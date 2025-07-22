from app.models.models import Category, Organization 

def category_to_dict(category):
    return {
        "id": category.id,
        "name": category.name,
        "org_id": category.org_id,
        "created_at": category.created_at.isoformat() if category.created_at else None,
    }

def category_organization_to_dict(category, organization):
    return {
        "id": category.id,
        "name": category.name,
        "org_id": category.org_id,
        "organization_name": organization.name if organization else None,
        "created_at": category.created_at.isoformat() if category.created_at else None,
    }

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
    return category

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

def get_joined_category_org(db, category_id: int):
    """
    Join Category and Organization on org_id

    Args:
        db: Database session.
        category_id: ID of the Category.

    Returns:
        A list of (Category, Organization) tuples
    """
    return db.query(Category, Organization).join(
        Category, Organization.id == Category.org_id).filter(
            Category.id == category_id
        ).first()

def join_org_and_to_dict(db, category_id: int):
    """
    Join Category and Organization on org_id and convert to dict.

    Args:
        db: Database session.
        category_id: ID of the Category.

    Returns:
        A dictionary representation of the joined data.
    """
    result = get_joined_category_org(db, category_id)
    if result:
        category, organization = result
        return category_organization_to_dict(category, organization)
    return None
