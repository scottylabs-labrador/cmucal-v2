from app.models.models import Organization 

def create_organization(db, name: str, description: str = None):
    """
    Create a new organization in the database.

    Args:
        db: Database session.
        name: Name of the organization.
        description: Description of the organization (optional).

    Returns:
        The created Organization object.
    """
    org = Organization(name=name, description=description)
    db.add(org)
    db.commit()
    db.refresh(org)
    return f"Event {org.id} created"

def get_organization_by_id(db, org_id: int):
    """
    Retrieve an organization by its ID.
    Args:
        db: Database session.
        org_id: ID of the organization.
    Returns:
        The Organization object if found, otherwise None.
    """
    return db.query(Organization).filter(Organization.id == org_id).first()

def delete_organization(db, org_id: int):
    """
    Delete an organization by its ID.

    Args:
        db: Database session.
        org_id: ID of the organization to delete.

    Returns:
        True if the organization was deleted, False if it was not found.
    """
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if org:
        db.delete(org)
        db.commit()
        return True
    return False
