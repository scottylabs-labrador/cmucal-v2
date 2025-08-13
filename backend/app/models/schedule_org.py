from app.models.models import ScheduleOrg

def create_schedule_org(db, schedule_id: int, org_id: int):
    """
    Add an organization to a schedule.
    
    Args:
        db: Database session.
        schedule_id: ID of the schedule.
        org_id: ID of the organization.
        
    Returns:
        The created ScheduleOrg object.
    """
    # Check if the relationship already exists
    existing = db.query(ScheduleOrg).filter(
        ScheduleOrg.schedule_id == schedule_id,
        ScheduleOrg.org_id == org_id
    ).first()
    
    if existing:
        return existing
        
    schedule_org = ScheduleOrg(schedule_id=schedule_id, org_id=org_id)
    db.add(schedule_org)
    db.commit()
    db.refresh(schedule_org)
    return schedule_org

def remove_schedule_org(db, schedule_id: int, org_id: int):
    """
    Remove an organization from a schedule.
    
    Args:
        db: Database session.
        schedule_id: ID of the schedule.
        org_id: ID of the organization.
        
    Returns:
        True if removed, False if not found.
    """
    schedule_org = db.query(ScheduleOrg).filter(
        ScheduleOrg.schedule_id == schedule_id,
        ScheduleOrg.org_id == org_id
    ).first()
    
    if schedule_org:
        db.delete(schedule_org)
        db.commit()
        return True
    return False