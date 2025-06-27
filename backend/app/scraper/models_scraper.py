from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

###########################################################################
# Core, shared value objects
###########################################################################

@dataclass
class RecurrenceRule:
    start_datetime: datetime
    frequency: str  # "DAILY", "WEEKLY", "MONTHLY"
    interval: int = 1  # Repeat every *interval* *frequency* units
    count: Optional[int] = None  # Total number of occurrences (mutually exclusive with *until*)
    until: Optional[datetime] = None  # Last possible occurrence (inclusive)
    by_day: Optional[List[str]] = None  # e.g. ["MO", "WE", "FR"]
    by_month_day: Optional[List[int]] = None  # e.g. [1, 15, 30]
    by_month: Optional[List[int]] = None  # e.g. [1, 6, 12]

    def to_json(self) -> Dict[str, Any]:
        d = asdict(self)
        # Serialize datetimes to ISO8601‑strings for JSON friendliness
        for key in ("start_datetime", "until"):
            if d[key] is not None:
                d[key] = d[key].isoformat()
        return d

###########################################################################
# Event model and specialised payloads per event type
###########################################################################

@dataclass
class CareerMeta:
    event_id: int
    host: str
    link: str
    registration_required: bool

    def to_json(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AcademicMeta:
    course_num: str
    course_name: str
    instructors: List[str]

    def to_json(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ClubMeta:
    # Placeholder for future club‑specific metadata
    pass


@dataclass
class Event:
    """Top-level canonical representation of an event row from the *events* table."""

    id: int
    title: str
    description: Optional[str]
    start_datetime: datetime
    end_datetime: datetime
    is_all_day: bool
    location: str
    source_url: Optional[str]
    event_type: str  # "CAREER", "ACADEMIC", "CLUB", etc.
    user_edited: bool = False
    org_id: Optional[int] = None
    category_id: Optional[int] = None
    last_updated_at: Optional[datetime] = None

    recurrence_rules: List[RecurrenceRule] = field(default_factory=list)

    # One — and only one — of the following *meta* payloads can be non‑None,
    # depending on *event_type*.
    career: Optional[CareerMeta] = None
    academic: Optional[AcademicMeta] = None
    club: Optional[ClubMeta] = None

    tags: List[str] = field(default_factory=list)

    #####################################################################
    # Serialisation helpers
    #####################################################################

    def to_json(self, include_meta: bool = True) -> Dict[str, Any]:
        base = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "start_datetime": self.start_datetime.isoformat(),
            "end_datetime": self.end_datetime.isoformat(),
            "is_all_day": self.is_all_day,
            "location": self.location,
            "source_url": self.source_url,
            "event_type": self.event_type,
            "user_edited": self.user_edited,
            "org_id": self.org_id,
            "category_id": self.category_id,
            "last_updated_at": self.last_updated_at.isoformat() if self.last_updated_at else None,
            "tags": self.tags,
            "recurrence_rules": [rule.to_json() for rule in self.recurrence_rules],
        }

        if include_meta:
            if self.event_type == "CAREER" and self.career:
                base["career"] = self.career.to_json()
            elif self.event_type == "ACADEMIC" and self.academic:
                base["academic"] = self.academic.to_json()
            elif self.event_type == "CLUB" and self.club:
                base["club"] = self.club.to_json()
        return base

    #####################################################################
    # Readable representation for debugging / CLI
    #####################################################################

    def __str__(self) -> str:  # pragma: no cover
        time_fmt = f"{self.start_datetime.isoformat()} — {self.end_datetime.isoformat()}"
        details = [f"[{self.event_type}] {self.title}", time_fmt, self.location]
        if self.tags:
            details.append("Tags: " + ", ".join(self.tags))
        if self.recurrence_rules:
            details.append(f"Recurs {len(self.recurrence_rules)} rule(s)")
        return " | ".join(details)

###########################################################################
# Discrete generated occurrences (denormalised view)
###########################################################################

@dataclass
class EventOccurrence:
    id: int
    parent_event_id: int
    title: str
    description: Optional[str]
    start_datetime: datetime
    end_datetime: datetime
    is_all_day: bool
    location: str
    source_url: Optional[str]
    user_edited: bool
    org_id: Optional[int]
    category_id: Optional[int]
    event_saved_at: Optional[datetime]
    recurrence: str  # "ONETIME", "RECURRING", "EXCEPTION"

    def to_json(self) -> Dict[str, Any]:
        d = asdict(self)
        # Convert datetimes to ISO strings for JSON compatibility
        for k in ("start_datetime", "end_datetime", "event_saved_at"):
            if d[k] is not None:
                d[k] = d[k].isoformat()
        return d

###########################################################################
# Tag model and reverse mapping table
###########################################################################

@dataclass
class Tag:
    id: int
    name: str

    def to_json(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EventTag:
    event_id: int
    tag_id: int

    def to_json(self) -> Dict[str, Any]:
        return asdict(self)

###########################################################################
# Convenience factories
###########################################################################

def create_career_event(row: Dict[str, Any], career_row: Dict[str, Any], tags: List[str], rules: List[Dict[str, Any]]) -> Event:
    """Helper that stitches an *events* row with its related *careers* and *recurrence_rules*."""
    event = Event(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        start_datetime=row["start_datetime"],
        end_datetime=row["end_datetime"],
        is_all_day=row["is_all_day"],
        location=row["location"],
        source_url=row["source_url"],
        event_type=row["event_type"],
        user_edited=row["user_edited"],
        org_id=row["org_id"],
        category_id=row["category_id"],
        last_updated_at=row.get("last_updated_at"),
        career=CareerMeta(
            host=career_row["host"],
            link=career_row["link"],
            registration_required=career_row["registration_required"],
        ),
        tags=tags,
        recurrence_rules=[RecurrenceRule(**rule) for rule in rules],
    )
    return event
