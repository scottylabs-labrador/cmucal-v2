from typing import List, Optional

from sqlalchemy import ARRAY, BigInteger, Boolean, Column, DateTime, Double, Enum, ForeignKeyConstraint, Identity, Numeric, PrimaryKeyConstraint, SmallInteger, Table, Text, Time, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import OID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime

class Base(DeclarativeBase):
    pass


class CrosslistGroups(Base):
    __tablename__ = 'crosslist_groups'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='crosslist_groups_pkey'),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))

    course_crosslist: Mapped[List['CourseCrosslist']] = relationship('CourseCrosslist', back_populates='group')


class Organizations(Base):
    __tablename__ = 'organizations'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='organizations_pkey'),
        UniqueConstraint('name', name='organizations_name_key')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    tags: Mapped[Optional[list]] = mapped_column(ARRAY(Text()))
    description: Mapped[Optional[str]] = mapped_column(Text)
    type: Mapped[Optional[str]] = mapped_column(Text)

    categories: Mapped[List['Categories']] = relationship('Categories', back_populates='org')
    courses: Mapped[List['Courses']] = relationship('Courses', back_populates='org')
    admins: Mapped[List['Admins']] = relationship('Admins', back_populates='org')
    events: Mapped[List['Events']] = relationship('Events', back_populates='org')
    schedule_orgs: Mapped[List['ScheduleOrgs']] = relationship('ScheduleOrgs', back_populates='org')
    event_occurrences: Mapped[List['EventOccurrences']] = relationship('EventOccurrences', back_populates='org')


t_pg_stat_statements = Table(
    'pg_stat_statements', Base.metadata,
    Column('userid', OID),
    Column('dbid', OID),
    Column('toplevel', Boolean),
    Column('queryid', BigInteger),
    Column('query', Text),
    Column('plans', BigInteger),
    Column('total_plan_time', Double(53)),
    Column('min_plan_time', Double(53)),
    Column('max_plan_time', Double(53)),
    Column('mean_plan_time', Double(53)),
    Column('stddev_plan_time', Double(53)),
    Column('calls', BigInteger),
    Column('total_exec_time', Double(53)),
    Column('min_exec_time', Double(53)),
    Column('max_exec_time', Double(53)),
    Column('mean_exec_time', Double(53)),
    Column('stddev_exec_time', Double(53)),
    Column('rows', BigInteger),
    Column('shared_blks_hit', BigInteger),
    Column('shared_blks_read', BigInteger),
    Column('shared_blks_dirtied', BigInteger),
    Column('shared_blks_written', BigInteger),
    Column('local_blks_hit', BigInteger),
    Column('local_blks_read', BigInteger),
    Column('local_blks_dirtied', BigInteger),
    Column('local_blks_written', BigInteger),
    Column('temp_blks_read', BigInteger),
    Column('temp_blks_written', BigInteger),
    Column('blk_read_time', Double(53)),
    Column('blk_write_time', Double(53)),
    Column('temp_blk_read_time', Double(53)),
    Column('temp_blk_write_time', Double(53)),
    Column('wal_records', BigInteger),
    Column('wal_fpi', BigInteger),
    Column('wal_bytes', Numeric),
    Column('jit_functions', BigInteger),
    Column('jit_generation_time', Double(53)),
    Column('jit_inlining_count', BigInteger),
    Column('jit_inlining_time', Double(53)),
    Column('jit_optimization_count', BigInteger),
    Column('jit_optimization_time', Double(53)),
    Column('jit_emission_count', BigInteger),
    Column('jit_emission_time', Double(53))
)


t_pg_stat_statements_info = Table(
    'pg_stat_statements_info', Base.metadata,
    Column('dealloc', BigInteger),
    Column('stats_reset', DateTime(True))
)


class Tags(Base):
    __tablename__ = 'tags'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='tags_pkey'),
        UniqueConstraint('name', name='tags_name_key')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    name: Mapped[str] = mapped_column(Text)

    event_tags: Mapped[List['EventTags']] = relationship('EventTags', back_populates='tag')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='users_pkey'),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    email: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    clerk_id: Mapped[Optional[str]] = mapped_column(Text)
    fname: Mapped[Optional[str]] = mapped_column(Text)
    lname: Mapped[Optional[str]] = mapped_column(Text)
    calendar_id: Mapped[Optional[str]] = mapped_column(Text)

    schedules: Mapped[List['Schedules']] = relationship('Schedules', back_populates='user')
    synced_events: Mapped[List['SyncedEvents']] = relationship('SyncedEvents', back_populates='user')
    admins: Mapped[List['Admins']] = relationship('Admins', back_populates='user')
    user_saved_events: Mapped[List['UserSavedEvents']] = relationship('UserSavedEvents', back_populates='user')


class Categories(Base):
    __tablename__ = 'categories'
    __table_args__ = (
        ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE', name='Categories_org_id_fkey'),
        PrimaryKeyConstraint('id', name='Categories_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    org_id: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))

    org: Mapped['Organizations'] = relationship('Organizations', back_populates='categories')
    admins: Mapped[List['Admins']] = relationship('Admins', back_populates='category')
    events: Mapped[List['Events']] = relationship('Events', back_populates='category')
    schedule_categories: Mapped[List['ScheduleCategories']] = relationship('ScheduleCategories', back_populates='category')
    event_occurrences: Mapped[List['EventOccurrences']] = relationship('EventOccurrences', back_populates='category')


class Courses(Base):
    __tablename__ = 'courses'
    __table_args__ = (
        ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE', name='courses_org_id_fkey'),
        PrimaryKeyConstraint('id', name='courses_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    course_number: Mapped[str] = mapped_column(Text)
    org_id: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))

    org: Mapped['Organizations'] = relationship('Organizations', back_populates='courses')
    course_crosslist: Mapped[List['CourseCrosslist']] = relationship('CourseCrosslist', back_populates='course')


class Schedules(Base):
    __tablename__ = 'schedules'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='schedules_user_id_fkey'),
        PrimaryKeyConstraint('id', name='schedules_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    user_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[Optional[str]] = mapped_column(Text)

    user: Mapped['Users'] = relationship('Users', back_populates='schedules')
    schedule_categories: Mapped[List['ScheduleCategories']] = relationship('ScheduleCategories', back_populates='schedule')
    schedule_orgs: Mapped[List['ScheduleOrgs']] = relationship('ScheduleOrgs', back_populates='schedule')
    user_saved_events: Mapped[List['UserSavedEvents']] = relationship('UserSavedEvents', back_populates='schedule')


class SyncedEvents(Base):
    __tablename__ = 'synced_events'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], onupdate='CASCADE', name='synced_events_user_id_fkey'),
        PrimaryKeyConstraint('id', name='synced_events_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    local_event_id: Mapped[str] = mapped_column(Text)
    google_event_id: Mapped[str] = mapped_column(Text)
    start: Mapped[str] = mapped_column(Text)
    synced_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    user_id: Mapped[int] = mapped_column(BigInteger)
    title: Mapped[Optional[str]] = mapped_column(Text)
    end: Mapped[Optional[str]] = mapped_column(Text)

    user: Mapped['Users'] = relationship('Users', back_populates='synced_events')


class Admins(Base):
    __tablename__ = 'admins'
    __table_args__ = (
        ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE', name='admins_category_id_fkey'),
        ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE', name='admins_org_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='admins_user_id_fkey'),
        PrimaryKeyConstraint('user_id', 'org_id', name='admins_pkey')
    )

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    org_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    role: Mapped[Optional[str]] = mapped_column(Text)
    category_id: Mapped[Optional[int]] = mapped_column(BigInteger)

    category: Mapped[Optional['Categories']] = relationship('Categories', back_populates='admins')
    org: Mapped['Organizations'] = relationship('Organizations', back_populates='admins')
    user: Mapped['Users'] = relationship('Users', back_populates='admins')


class CourseCrosslist(Base):
    __tablename__ = 'course_crosslist'
    __table_args__ = (
        ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE', name='course_crosslist_course_id_fkey'),
        ForeignKeyConstraint(['group_id'], ['crosslist_groups.id'], ondelete='CASCADE', name='course_crosslist_group_id_fkey'),
        PrimaryKeyConstraint('id', name='course_crosslist_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    course_id: Mapped[int] = mapped_column(BigInteger)
    group_id: Mapped[int] = mapped_column(BigInteger)

    course: Mapped['Courses'] = relationship('Courses', back_populates='course_crosslist')
    group: Mapped['CrosslistGroups'] = relationship('CrosslistGroups', back_populates='course_crosslist')


class Events(Base):
    __tablename__ = 'events'
    __table_args__ = (
        ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE', name='events_category_id_fkey'),
        ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE', name='events_org_id_fkey'),
        PrimaryKeyConstraint('id', name='events_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    title: Mapped[str] = mapped_column(Text)
    start_datetime: Mapped[datetime.datetime] = mapped_column(DateTime(True))
    end_datetime: Mapped[datetime.datetime] = mapped_column(DateTime(True))
    is_all_day: Mapped[bool] = mapped_column(Boolean)
    location: Mapped[str] = mapped_column(Text)
    org_id: Mapped[int] = mapped_column(BigInteger)
    category_id: Mapped[int] = mapped_column(BigInteger)
    last_updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    event_type: Mapped[Optional[str]] = mapped_column(Text)
    user_edited: Mapped[Optional[list]] = mapped_column(ARRAY(BigInteger()))
    ical_uid: Mapped[Optional[str]] = mapped_column(Text)
    ical_sequence: Mapped[Optional[int]] = mapped_column(BigInteger)
    ical_last_modified: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    category: Mapped['Categories'] = relationship('Categories', back_populates='events')
    org: Mapped['Organizations'] = relationship('Organizations', back_populates='events')
    event_occurrences: Mapped[List['EventOccurrences']] = relationship('EventOccurrences', back_populates='event')
    event_tags: Mapped[List['EventTags']] = relationship('EventTags', back_populates='event')
    recurrence_rules: Mapped[List['RecurrenceRules']] = relationship('RecurrenceRules', back_populates='event')
    user_saved_events: Mapped[List['UserSavedEvents']] = relationship('UserSavedEvents', back_populates='event')


class ScheduleCategories(Base):
    __tablename__ = 'schedule_categories'
    __table_args__ = (
        ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE', name='user_saved_categories_category_id_fkey'),
        ForeignKeyConstraint(['schedule_id'], ['schedules.id'], ondelete='CASCADE', name='user_saved_categories_schedule_id_fkey'),
        PrimaryKeyConstraint('schedule_id', 'category_id', name='user_saved_categories_pkey')
    )

    schedule_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    category_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    category: Mapped['Categories'] = relationship('Categories', back_populates='schedule_categories')
    schedule: Mapped['Schedules'] = relationship('Schedules', back_populates='schedule_categories')


class ScheduleOrgs(Base):
    __tablename__ = 'schedule_orgs'
    __table_args__ = (
        ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE', name='schedule_orgs_org_id_fkey'),
        ForeignKeyConstraint(['schedule_id'], ['schedules.id'], ondelete='CASCADE', name='schedule_orgs_schedule_id_fkey'),
        PrimaryKeyConstraint('schedule_id', 'org_id', name='schedule_orgs_pkey')
    )

    schedule_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    org_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))

    org: Mapped['Organizations'] = relationship('Organizations', back_populates='schedule_orgs')
    schedule: Mapped['Schedules'] = relationship('Schedules', back_populates='schedule_orgs')


class Academics(Events):
    __tablename__ = 'academics'
    __table_args__ = (
        ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE', name='academics_event_id_fkey'),
        PrimaryKeyConstraint('event_id', name='academics_pkey')
    )

    event_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    course_num: Mapped[str] = mapped_column(Text)
    course_name: Mapped[str] = mapped_column(Text)
    instructors: Mapped[Optional[list]] = mapped_column(ARRAY(Text()))


class Careers(Events):
    __tablename__ = 'careers'
    __table_args__ = (
        ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE', name='careers_event_id_fkey'),
        PrimaryKeyConstraint('event_id', name='careers_pkey')
    )

    event_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    host: Mapped[Optional[str]] = mapped_column(Text)
    link: Mapped[Optional[str]] = mapped_column(Text)
    registration_required: Mapped[Optional[bool]] = mapped_column(Boolean)


class Clubs(Events):
    __tablename__ = 'clubs'
    __table_args__ = (
        ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE', name='clubs_event_id_fkey'),
        PrimaryKeyConstraint('event_id', name='clubs_pkey')
    )

    event_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)


class EventOccurrences(Base):
    __tablename__ = 'event_occurrences'
    __table_args__ = (
        ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE', name='event_occurrences_category_id_fkey'),
        ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE', name='event_occurrences_event_id_fkey'),
        ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE', name='event_occurrences_org_id_fkey'),
        PrimaryKeyConstraint('id', name='event_occurrences_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    start_datetime: Mapped[datetime.datetime] = mapped_column(DateTime(True))
    end_datetime: Mapped[datetime.datetime] = mapped_column(DateTime(True))
    location: Mapped[str] = mapped_column(Text)
    is_all_day: Mapped[bool] = mapped_column(Boolean)
    event_id: Mapped[int] = mapped_column(BigInteger)
    event_saved_at: Mapped[datetime.datetime] = mapped_column(DateTime(True))
    title: Mapped[str] = mapped_column(Text)
    org_id: Mapped[int] = mapped_column(BigInteger)
    category_id: Mapped[int] = mapped_column(BigInteger)
    recurrence: Mapped[str] = mapped_column(Enum('ONETIME', 'RECURRING', 'EXCEPTION', name='recurrence_type'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    user_edited: Mapped[Optional[list]] = mapped_column(ARRAY(BigInteger()))

    category: Mapped['Categories'] = relationship('Categories', back_populates='event_occurrences')
    event: Mapped['Events'] = relationship('Events', back_populates='event_occurrences')
    org: Mapped['Organizations'] = relationship('Organizations', back_populates='event_occurrences')


class EventTags(Base):
    __tablename__ = 'event_tags'
    __table_args__ = (
        ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE', name='event_tags_event_id_fkey'),
        ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE', name='event_tags_tag_id_fkey'),
        PrimaryKeyConstraint('event_id', 'tag_id', name='event_tags_pkey')
    )

    event_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tag_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))

    event: Mapped['Events'] = relationship('Events', back_populates='event_tags')
    tag: Mapped['Tags'] = relationship('Tags', back_populates='event_tags')


class RecurrenceRules(Base):
    __tablename__ = 'recurrence_rules'
    __table_args__ = (
        ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE', name='recurrence_rules_event_id_fkey'),
        PrimaryKeyConstraint('id', name='recurrence_rules_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    frequency: Mapped[str] = mapped_column(Enum('DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY', name='frequency_type'))
    interval: Mapped[int] = mapped_column(BigInteger)
    event_id: Mapped[int] = mapped_column(BigInteger)
    start_datetime: Mapped[datetime.datetime] = mapped_column(DateTime(True))
    count: Mapped[Optional[int]] = mapped_column(BigInteger)
    until: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    by_day: Mapped[Optional[list]] = mapped_column(ARRAY(Text()))
    by_month: Mapped[Optional[int]] = mapped_column(SmallInteger)
    by_month_day: Mapped[Optional[int]] = mapped_column(SmallInteger)
    orig_until: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    event: Mapped['Events'] = relationship('Events', back_populates='recurrence_rules')
    event_overrides: Mapped[List['EventOverrides']] = relationship('EventOverrides', back_populates='rrule')
    recurrence_exdates: Mapped[List['RecurrenceExdates']] = relationship('RecurrenceExdates', back_populates='rrule')
    recurrence_rdates: Mapped[List['RecurrenceRdates']] = relationship('RecurrenceRdates', back_populates='rrule')


class UserSavedEvents(Base):
    __tablename__ = 'user_saved_events'
    __table_args__ = (
        ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE', name='user_saved_events_event_id_fkey'),
        ForeignKeyConstraint(['schedule_id'], ['schedules.id'], ondelete='CASCADE', name='user_saved_events_schedule_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='user_saved_events_user_id_fkey'),
        PrimaryKeyConstraint('user_id', 'event_id', name='user_saved_events_pkey'),
        UniqueConstraint('google_event_id', name='user_saved_events_google_event_id_key')
    )

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    event_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    google_event_id: Mapped[str] = mapped_column(Text)
    saved_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    schedule_id: Mapped[Optional[int]] = mapped_column(BigInteger)

    event: Mapped['Events'] = relationship('Events', back_populates='user_saved_events')
    schedule: Mapped[Optional['Schedules']] = relationship('Schedules', back_populates='user_saved_events')
    user: Mapped['Users'] = relationship('Users', back_populates='user_saved_events')


class EventOverrides(Base):
    __tablename__ = 'event_overrides'
    __table_args__ = (
        ForeignKeyConstraint(['rrule_id'], ['recurrence_rules.id'], ondelete='CASCADE', name='event_overrides_rrule_id_fkey'),
        PrimaryKeyConstraint('id', name='event_overrides_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    rrule_id: Mapped[int] = mapped_column(BigInteger)
    recurrence_date: Mapped[datetime.time] = mapped_column(Time(True))
    new_start: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    new_end: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    new_title: Mapped[Optional[str]] = mapped_column(Text)
    new_description: Mapped[Optional[str]] = mapped_column(Text)
    new_location: Mapped[Optional[str]] = mapped_column(Text)

    rrule: Mapped['RecurrenceRules'] = relationship('RecurrenceRules', back_populates='event_overrides')


class RecurrenceExdates(Base):
    __tablename__ = 'recurrence_exdates'
    __table_args__ = (
        ForeignKeyConstraint(['rrule_id'], ['recurrence_rules.id'], ondelete='CASCADE', name='recurrence_exdates_rrule_id_fkey'),
        PrimaryKeyConstraint('id', name='recurrence_exdates_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    rrule_id: Mapped[int] = mapped_column(BigInteger)
    exdate: Mapped[datetime.datetime] = mapped_column(DateTime(True))

    rrule: Mapped['RecurrenceRules'] = relationship('RecurrenceRules', back_populates='recurrence_exdates')


class RecurrenceRdates(Base):
    __tablename__ = 'recurrence_rdates'
    __table_args__ = (
        ForeignKeyConstraint(['rrule_id'], ['recurrence_rules.id'], ondelete='CASCADE', name='recurrence_rdates_rrule_id_fkey'),
        PrimaryKeyConstraint('id', name='recurrence_rdates_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    rrule_id: Mapped[int] = mapped_column(BigInteger)
    rdate: Mapped[datetime.datetime] = mapped_column(DateTime(True))

    rrule: Mapped['RecurrenceRules'] = relationship('RecurrenceRules', back_populates='recurrence_rdates')
