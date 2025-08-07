from typing import List
from app.models.models import Course, CrosslistGroup, CourseCrosslist, Organization
from app.utils.course_data import get_course_data

def create_organization(db, name: str, description: str = None, type: str = None):
    """
    Create a new organization in the database.

    Args:
        db: Database session.
        name: Name of the organization.
        description: Description of the organization (optional).

    Returns:
        The created Organization object.
    """
    org = Organization(name=name, description=description, type=type)
    db.add(org)
    db.commit()
    return org

def get_orgs_by_type(db, org_type: str):
    """
    Fetch all organizations of a specific type.
    """
    return db.query(Organization).filter(Organization.type == org_type).all()

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


def create_course_orgs_from_file(db):
    data = get_course_data()
    created_orgs = []

    for record in data:
        course_number = record.get("course_number")
        title = record.get("title")
        crosslisted = record.get("crosslisted", [])

        if not course_number or not title:
            continue

        formatted_course_number = course_number[:2] + '-' + course_number[2:]
        org_name = f"{formatted_course_number} {title}"
        org = Organization(name=org_name, type="COURSE", description=title)
        db.add(org)
        db.flush()

        course = db.query(Course).filter_by(course_number=course_number).first()
        if not course:
            course = Course(course_number=course_number, org_id=org.id)
            db.add(course)
            db.flush()
        else:
            if course.org_id != org.id:
                course.org_id = org.id
                db.add(course)
                db.flush()

        if crosslisted:
            crosslist_group = CrosslistGroup(name=title)
            db.add(crosslist_group)
            db.flush()
            print(f"✅ Created crosslist group: {crosslist_group.id}")
            print(f"✅ Linking course {course.id} to group {crosslist_group.id}")

            crosslist_course = CourseCrosslist(course_id=course.id, group_id=crosslist_group.id)
            db.add(crosslist_course)
            db.flush()

            for alt_course_number in crosslisted:
                alt_course = db.query(Course).filter_by(course_number=alt_course_number).first()
                if not alt_course:
                    alt_course = Course(course_number=alt_course_number, org_id=org.id)
                    db.add(alt_course)
                    db.flush()
                db.add(CourseCrosslist(course_id=alt_course.id, group_id=crosslist_group.id))

        created_orgs.append({
            "org_name": org_name,
            "org_id": org.id,
            "course_number": course_number,
        })

    return created_orgs

