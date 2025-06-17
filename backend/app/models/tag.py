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
    db.commit()
    db.refresh(tag)
    return f"Tag {tag.id} created"