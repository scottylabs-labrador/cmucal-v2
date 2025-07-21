from typing import List, Optional

from sqlalchemy import ARRAY, BigInteger, Boolean, Column, Date, DateTime, Double, Enum, ForeignKeyConstraint, SmallInteger, Identity, Numeric, PrimaryKeyConstraint, Table, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import OID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime
from app.services.db import Base
from app.models.enums import FrequencyType, RecurrenceType

class Academic(Base):
    __tablename__ = 'academics'
    __table_args__ = (
        ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE', name='academics_event_id_fkey'),
        PrimaryKeyConstraint('event_id', name='academics_pkey')
    )

    event_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    course_num: Mapped[str] = mapped_column(Text)
    course_name: Mapped[str] = mapped_column(Text)
    instructors: Mapped[Optional[list]] = mapped_column(ARRAY(Text()))


class Career(Base):
    __tablename__ = 'careers'
    __table_args__ = (
        ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE', name='careers_event_id_fkey'),
        PrimaryKeyConstraint('event_id', name='careers_pkey')
    )

    event_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    host: Mapped[Optional[str]] = mapped_column(Text)
    link: Mapped[Optional[str]] = mapped_column(Text)
    registration_required: Mapped[Optional[bool]] = mapped_column(Boolean)


class Organization(Base):
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
    crosslisted: Mapped[Optional[list]] = mapped_column(ARRAY(Text()))

    admins: Mapped[List['Admin']] = relationship('Admin', back_populates='org')
    categories: Mapped[List['Category']] = relationship('Category', back_populates='org')
    events: Mapped[List['Event']] = relationship('Event', back_populates='org')
    event_occurrences: Mapped[List['EventOccurrence']] = relationship('EventOccurrence', back_populates='org')


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


class Tag(Base):
    __tablename__ = 'tags'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='tags_pkey'),
        UniqueConstraint('name', name='tags_name_key')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    name: Mapped[str] = mapped_column(Text)

    event_tags: Mapped[List['EventTag']] = relationship('EventTag', back_populates='tag')


class User(Base):
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

    admins: Mapped[List['Admin']] = relationship('Admin', back_populates='user')
    schedules: Mapped[List['Schedule']] = relationship('Schedule', back_populates='user')
    synced_events: Mapped[List['SyncedEvent']] = relationship('SyncedEvent', back_populates='user')
    user_saved_events: Mapped[List['UserSavedEvent']] = relationship('UserSavedEvent', back_populates='user')


class Admin(Base):
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

    category: Mapped[Optional['Category']] = relationship('Category', back_populates='admins')
    org: Mapped['Organization'] = relationship('Organization', back_populates='admins')
    user: Mapped['User'] = relationship('User', back_populates='admins')


class Category(Base):
    __tablename__ = 'categories'
    __table_args__ = (
        ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE', name='Category_org_id_fkey'),
        PrimaryKeyConstraint('id', name='Category_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    org_id: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))

    org: Mapped['Organization'] = relationship('Organization', back_populates='categories')
    admins: Mapped[List['Admin']] = relationship('Admin', back_populates='category')
    events: Mapped[List['Event']] = relationship('Event', back_populates='category')
    schedule_categories: Mapped[List['ScheduleCategory']] = relationship('ScheduleCategory', back_populates='category')
    event_occurrences: Mapped[List['EventOccurrence']] = relationship('EventOccurrence', back_populates='category')


class Schedule(Base):
    __tablename__ = 'schedules'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='schedules_user_id_fkey'),
        PrimaryKeyConstraint('id', name='schedules_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    user_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[Optional[str]] = mapped_column(Text)

    user: Mapped['User'] = relationship('User', back_populates='schedules')
    schedule_categories: Mapped[List['ScheduleCategory']] = relationship('ScheduleCategory', back_populates='schedule')


class SyncedEvent(Base):
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

    user: Mapped['User'] = relationship('User', back_populates='synced_events')


class Event(Base):
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
    user_edited: Mapped[Optional[list]] = mapped_column(ARRAY(BigInteger()))
    org_id: Mapped[int] = mapped_column(BigInteger)
    category_id: Mapped[int] = mapped_column(BigInteger)
    description: Mapped[Optional[str]] = mapped_column(Text)
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    event_type: Mapped[Optional[str]] = mapped_column(Text)
    last_updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))

    category: Mapped['Category'] = relationship('Category', back_populates='events')
    org: Mapped['Organization'] = relationship('Organization', back_populates='events')
    event_occurrences: Mapped[List['EventOccurrence']] = relationship('EventOccurrence', back_populates='event')
    event_tags: Mapped[List['EventTag']] = relationship('EventTag', back_populates='event')
    recurrence_rules: Mapped[List['RecurrenceRule']] = relationship('RecurrenceRule', back_populates='event')
    user_saved_events: Mapped[List['UserSavedEvent']] = relationship('UserSavedEvent', back_populates='event')


class ScheduleCategory(Base):
    __tablename__ = 'schedule_categories'
    __table_args__ = (
        ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE', name='schedule_categories_category_id_fkey'),
        ForeignKeyConstraint(['schedule_id'], ['schedules.id'], ondelete='CASCADE', name='schedule_categories_category_id_fkey'),
        PrimaryKeyConstraint('schedule_id', 'category_id', name='schedule_categories_pkey')
    )

    schedule_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    category_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    category: Mapped['Category'] = relationship('Category', back_populates='schedule_categories')
    schedule: Mapped['Schedule'] = relationship('Schedule', back_populates='schedule_categories')


class Club(Base):
    __tablename__ = 'clubs'
    __table_args__ = (
        ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE', name='clubs_event_id_fkey'),
        PrimaryKeyConstraint('event_id', name='clubs_pkey')
    )

    event_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)


class EventOccurrence(Base):
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
    user_edited: Mapped[Optional[list]] = mapped_column(ARRAY(BigInteger()))
    event_id: Mapped[int] = mapped_column(BigInteger)
    event_saved_at: Mapped[datetime.datetime] = mapped_column(DateTime(True))
    title: Mapped[str] = mapped_column(Text)
    org_id: Mapped[int] = mapped_column(BigInteger)
    category_id: Mapped[int] = mapped_column(BigInteger)
    recurrence: Mapped[str] = mapped_column(Enum(RecurrenceType, name='recurrence_type', create_type=False))
    description: Mapped[Optional[str]] = mapped_column(Text)
    source_url: Mapped[Optional[str]] = mapped_column(Text)

    category: Mapped['Category'] = relationship('Category', back_populates='event_occurrences')
    event: Mapped['Event'] = relationship('Event', back_populates='event_occurrences')
    org: Mapped['Organization'] = relationship('Organization', back_populates='event_occurrences')


class EventTag(Base):
    __tablename__ = 'event_tags'
    __table_args__ = (
        ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE', name='event_tags_event_id_fkey'),
        ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE', name='event_tags_tag_id_fkey'),
        PrimaryKeyConstraint('event_id', 'tag_id', name='event_tags_pkey')
    )

    event_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tag_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))

    event: Mapped['Event'] = relationship('Event', back_populates='event_tags')
    tag: Mapped['Tag'] = relationship('Tag', back_populates='event_tags')


class RecurrenceRule(Base):
    __tablename__ = 'recurrence_rules'
    __table_args__ = (
        ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE', name='recurrence_rules_event_id_fkey'),
        PrimaryKeyConstraint('id', name='recurrence_rules_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    event_id: Mapped[int] = mapped_column(BigInteger)
    frequency: Mapped[str] = mapped_column(Enum(FrequencyType, name='frequency_type', create_type=False))
    interval: Mapped[int] = mapped_column(BigInteger)
    start_datetime: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    count: Mapped[Optional[int]] = mapped_column(BigInteger)
    until: Mapped[Optional[datetime.date]] = mapped_column(DateTime(timezone=True))
    by_month: Mapped[Optional[list]] = mapped_column(SmallInteger)
    by_month_day: Mapped[Optional[list]] = mapped_column(SmallInteger)
    by_day: Mapped[Optional[list]] = mapped_column(ARRAY(Text()))
    orig_until: Mapped[Optional[datetime.date]] = mapped_column(DateTime(timezone=True), nullable=True)

    event: Mapped['Event'] = relationship('Event', back_populates='recurrence_rules')


class UserSavedEvent(Base):
    __tablename__ = 'user_saved_events'
    __table_args__ = (
        ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE', name='user_saved_events_event_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='user_saved_events_user_id_fkey'),
        PrimaryKeyConstraint('user_id', 'event_id', name='user_saved_events_pkey'),
        UniqueConstraint('google_event_id', name='user_saved_events_google_event_id_key')
    )

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    event_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    google_event_id: Mapped[str] = mapped_column(Text)
    saved_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))

    event: Mapped['Event'] = relationship('Event', back_populates='user_saved_events')
    user: Mapped['User'] = relationship('User', back_populates='user_saved_events')
