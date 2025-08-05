# app/cli.py

import click
from flask.cli import with_appcontext
from app.services.db import SessionLocal
from app.models.organization import create_course_orgs_from_file

@click.command("import-courses")
@with_appcontext
def import_courses_command():
    with SessionLocal() as db:
        try:
            result = create_course_orgs_from_file(db)
            db.commit()
            click.echo(f"✅ Imported {len(result)} course orgs successfully.")
        except Exception as e:
            db.rollback()
            click.echo(f"❌ Error: {e}")
