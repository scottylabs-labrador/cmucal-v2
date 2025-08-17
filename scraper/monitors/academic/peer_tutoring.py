

import requests
import bs4
from monitors.base_scraper import BaseScraper
from models import CourseResource, ResourceEvent
import time
import re
import datetime

class PeerTutoringScraper(BaseScraper):
    def __init__(self, db):
        super().__init__(db, "Peer Tutoring", "WCOnline")
    
    def scrape(self):
        # This doesn't work anymore after they switched to SSO login. Have to find workaround.
        # If I pass in wconline_session Cookie, seems to work (no need for X-CRSF-TOKEN). We might have to hardcode -- how long do session cookies last though?
        email = "dkathein@andrew.cmu.edu"
        password = "CMUCalToTheMoon"

        link = "https://cmu.mywconline.net/index.php"
        s = requests.Session()
        r = s.get(link, headers=self.headers)

        payload = {
            "username": email,
            "password": password,
            "scheduleid": "sc64da3ea4c19b9",
            "setCookie": "1",
            "submit": "login"
        }
        r = s.post(link, data=payload, headers=self.headers)
        soup = bs4.BeautifulSoup(r.text, 'html.parser')

        courses = soup.find('select', id="limfoc").findAll('option')[1:]
        resources = []
        for course in courses:
            link = "https://cmu.mywconline.net/" + course.get("value")
            course = course.text.strip().rstrip(" Only")
            course_id, course_name = course.split(" ", 1)
            course_id = course_id[:2] + "-" + course_id[2:]
            professor = None
            print(f"{course_id} | {course_name} | {link}")

            r = s.get(link, headers=self.headers)
            soup = bs4.BeautifulSoup(r.text, 'html.parser')
            days = soup.findAll("div", style="overflow-x:auto;")
            
            appt_count = 0
            instructor_events = {}
            for day in days:
                weekday = day.find("th", class_="col_first fw-normal").text.strip()
                available_appts = day.findAll("td", {"aria-label": "Open/Available Appointment Slot"})
                for appt in available_appts:
                    apptdata = appt.get("title").strip()

                    time1 = apptdata.split("reserve <strong>")[1].split("<")[0]
                    month_day_yr = apptdata.split("on <strong>")[1].split("<")[0] + ", " + str(datetime.datetime.now().year)
                    start_datetime = datetime.datetime.strptime(f"{month_day_yr} {time1}", "%B %d, %Y %I:%M %p")
                    end_datetime = start_datetime + datetime.timedelta(hours=1)

                    instructor = apptdata.split("with <strong>")[1].split("<")[0]
                    
                    # Create ResourceEvent
                    event = ResourceEvent(
                        start_datetime=start_datetime,
                        end_datetime=end_datetime,
                        location="WCOnline",
                        recurrence=None  # No recurrence
                    )

                    if instructor not in instructor_events:
                        instructor_events[instructor] = []
                    instructor_events[instructor].append(event)

                    appt_count += 1
            
            for instructor, events in instructor_events.items():
                resource = CourseResource(
                    resource_type="Peer Tutoring",
                    resource_source=self.resource_source,
                    course_id=course_id,
                    course_name=course_name,
                    professor=professor,
                    instructor=instructor,
                    events=events
                )
                resources.append(resource)

            print(f"Added {appt_count} appts.")
            time.sleep(0.5)
            #if appt_count > 40:
            #    break
        
        # Update the database
        unique_keys = ["resource_type", "course_id", "instructor"]
        self.update_database(resources, "academic_events", unique_keys)