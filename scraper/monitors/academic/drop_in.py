

import requests
import bs4
from monitors.base_scraper import BaseScraper
from models import CourseResource, ResourceEvent
import time
import re
import datetime

class DropInScraper(BaseScraper):
    def __init__(self, db):
        super().__init__(db, "Drop In Tutoring", "CMU Drop In Website")
    
    def scrape(self):
        link = "https://www.cmu.edu/student-success/programs/tutoring.html"
        r = requests.get(link, headers=self.headers)
        soup = bs4.BeautifulSoup(r.text, 'html.parser')

        table = soup.find('table', id="dropintable")
        #print(table)

        if table is None:
            raise Exception("No table exists on Drop In website. Could be due to lack of courses (Summer time)")
        
        resources = []
        for i, row in enumerate(table.find_all('tr')):
            if i != 0:
                data = row.find_all('th') + row.find_all('td')

                course_nameids = data[0].text.strip()
                courses_name_ids_parsed = re.findall(r'(\d{2}-\d{3})\s(.*?)(?=(\d{2}-\d{3})|$)', course_nameids)

                # Default: 8-10pm
                start_time = datetime.time(hour=20)
                end_time = datetime.time(hour=22)
                weekday = data[1].text.strip()
                
                if "(" in weekday:
                    new_time = weekday.split("(", 1)[1].split(")")[0].strip().replace(" ", "").split("-")
                    try:
                        start_time = datetime.datetime.strptime(new_time[0], "%I:%M%p").time()
                    except ValueError:
                        start_time = datetime.datetime.strptime(new_time[0], "%I%p").time()
                    
                    try:
                        end_time = datetime.datetime.strptime(new_time[1], "%I:%M%p").time()
                    except ValueError:
                        end_time = datetime.datetime.strptime(new_time[1], "%I%p").time()
                    
                    weekday = weekday.split("(")[0].strip()
                
                location = data[2].text.strip()
                tutor = data[3].text.strip()

                weekday = time.strptime(weekday.rstrip("s"), "%A").tm_wday
                next_date = self.get_next_weekday(weekday)

                # Combine date with start and end times to create datetime objects
                start_datetime = datetime.datetime.combine(next_date, start_time)
                end_datetime = datetime.datetime.combine(next_date, end_time)

                recurrence = {
                    "frequency": "weekly",
                    "interval": 1,
                    "weekdays": [weekday]
                }

                # Create the ResourceEvent with recurrence
                event = ResourceEvent(
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    location=location,
                    recurrence=recurrence
                )

                # For each course, create a CourseResource
                for course in courses_name_ids_parsed:
                    course_id = course[0]
                    course_name = course[1].strip().strip("&").strip()
                    resource = CourseResource(
                        resource_type="Drop In Tutoring",
                        resource_source=self.resource_source,
                        course_id=course_id,
                        course_name=course_name,
                        professor=None,  # Assuming no professor info for tutoring
                        instructor=tutor,
                        events=[event]
                    )
                    resources.append(resource)
        
        # Update the database
        unique_keys = ["resource_type", "course_id", "instructor"]
        self.update_database(resources, "academic_events", unique_keys)