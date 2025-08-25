

import requests
import bs4
from monitors.base_scraper import BaseScraper
from models import CourseResource, ResourceEvent
import time
import re
import datetime

class OfficeHoursScraper(BaseScraper):
    def __init__(self, db):
        super().__init__(db, "Office Hours", "15122 Office Hours")
    
    def scrape(self):
        print("Running Office Hours scraper...")
        # URL to fetch the 15-122 office hours from Google Calendar API
        url = "https://clients6.google.com/calendar/v3/calendars/andrew.cmu.edu_oclvc5roik51hr1ak1i29iavd8@group.calendar.google.com/events"
        params = {
            "calendarId": "andrew.cmu.edu_oclvc5roik51hr1ak1i29iavd8@group.calendar.google.com",
            "singleEvents": "true",
            "eventTypes": ["default", "focusTime", "outOfOffice"],
            "timeZone": "America/New_York",
            "maxAttendees": 1,
            "maxResults": 250,
            "sanitizeHtml": "true",
            "timeMin": datetime.datetime.utcnow().isoformat() + "Z",
            "timeMax": (datetime.datetime.utcnow() + datetime.timedelta(days=21)).isoformat() + "Z",
            "key": "AIzaSyBNlYH01_9Hc5S1J9vuFmu2nUqBZJNAXxs",
            "$unique": "gc237"
        }

        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching office hours data: {e}")
            return

        items = data.get("items", [])
        resources = []

        for item in items:
            summary = item.get("summary", "")
            description = item.get("description", "")
            start = item.get("start", {}).get("dateTime")
            end = item.get("end", {}).get("dateTime")

            if not start or not end:
                continue

            # Parse start and end times
            start_datetime = datetime.datetime.fromisoformat(start)
            end_datetime = datetime.datetime.fromisoformat(end)

            # Assume course_id and course_name are known
            course_id = "15-122"
            course_name = "Principles of Imperative Computation"
            professor = "Iliano Cervesato"
            instructor = item.get("location", "").lstrip('(').rstrip(')')
            if not instructor:
                instructor = "TAs"
            location = item.get("summary", "")

            # Create ResourceEvent
            event = ResourceEvent(
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                location=location,
                recurrence=None
            )

            # Check if a resource for this instructor already exists
            existing_resource = next((res for res in resources if res.instructor == instructor), None)
            if existing_resource:
                existing_resource.events.append(event)
            else:
                resource = CourseResource(
                    resource_type="OH",
                    resource_source = "15122 OH Calendar",
                    course_id=course_id,
                    course_name=course_name,
                    professor=professor,
                    instructor=instructor,
                    events=[event]
                )
                resources.append(resource)

        # Update the database
        unique_keys = ["resource_type", "course_id", "instructor"]
        self.update_database(resources, "academic_events", unique_keys)