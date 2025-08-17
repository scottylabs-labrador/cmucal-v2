from datetime import datetime
from typing import Optional, List, Dict

class ResourceEvent:
    def __init__(
        self,
        start_datetime: datetime,
        end_datetime: datetime,
        location: str,
        recurrence: Optional[Dict] = None  # Defines recurrence pattern
    ):
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.location = location
        self.recurrence = recurrence

    def to_json(self):
        json = {
            "start_datetime": self.start_datetime,
            "end_datetime": self.end_datetime,
            "location": self.location,
            "recurrence": self.recurrence
        }
        return json

    def __str__(self):
        recurrence_str = f" | Recurs: {self.recurrence}" if self.recurrence else ""
        return f"{self.start_datetime.isoformat()} - {self.end_datetime.isoformat()} | {self.location}{recurrence_str}"

class CourseResource:
    def __init__(
        self,
        resource_type: str,  # "Office Hours", "Supplemental Instruction", "Peer Tutoring", "Drop In Tutoring"
        resource_source: str, # "122 OH Calendar", "CMU SI Page", etc.
        course_id: str,
        course_name: str,
        professor: str,
        instructor: str,
        events: List[ResourceEvent]
    ):
        self.resource_type = resource_type
        self.resource_source = resource_source
        self.course_id = course_id
        self.course_name = course_name
        self.professor = professor
        self.instructor = instructor
        self.events = events

    def to_json(self):
        json = {
            "resource_type": self.resource_type,
            "resource_source": self.resource_source,
            "course_id": self.course_id,
            "course_name": self.course_name,
            "professor": self.professor,
            "instructor": self.instructor,
            "events": [event.to_json() for event in self.events]
        }
        return json

    def __str__(self):
        events_str = '\n'.join([str(e) for e in self.events])
        return (
            f"{self.resource_type} - {self.resource_source}: {self.course_id} | {self.course_name}\n"
            f"P: {self.professor} | I: {self.instructor}\n{events_str}"
        )

class OtherResource:
    def __init__(
        self,
        resource_type: str,  # "Career", "Club"
        resource_source: str,  # "Handshake", "TartanConnect Website"
        event_name: str,
        event_host: str,
        events: List[ResourceEvent],
        categories: List[str],
        metadata: Optional[Dict] = None  # Additional metadata specific to the resource type
    ):
        self.resource_type = resource_type
        self.resource_source = resource_source
        self.event_name = event_name
        self.event_host = event_host
        self.events = events
        self.categories = categories
        self.metadata = metadata or {}

    def to_json(self):
        json = {
            "resource_type": self.resource_type,
            "resource_source": self.resource_source,
            "event_name": self.event_name,
            "event_host": self.event_host,
            "events": [event.to_json() for event in self.events],
            "categories": self.categories
        }
        # Add metadata if present
        if self.metadata:
            json.update(self.metadata)
        return json

    def __str__(self):
        events_str = '\n'.join([str(e) for e in self.events])
        categories_str = ', '.join(self.categories)
        metadata_str = f"\nMetadata: {self.metadata}" if self.metadata else ""
        return (
            f"{self.resource_type} - {self.resource_source}: {self.event_name} | {self.event_host}\n"
            f"Categories: {categories_str}\n{events_str}{metadata_str}"
        )