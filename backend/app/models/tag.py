from app.models.models import Tag

def save_tag(db, name: str):
    """
    Save a new tag in the database.

    Args:
        db: Database session.
        name: Name of the tag.

    Returns:
        The created Tag object.
    """
    tag = Tag(name=name)
    db.add(tag)
    db.flush() 
    db.refresh(tag)
    return tag

def get_tag_by_name(db, name: str):
    """
    Retrieve a tag by its name.
    Args:
        db: Database session.
        name: Name of the tag.
    Returns:
        The Tag object if found, otherwise None.
    """
    return db.query(Tag).filter(Tag.name == name).first()