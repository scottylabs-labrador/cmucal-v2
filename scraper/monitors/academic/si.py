
import requests
import bs4
from monitors.base_scraper import BaseScraper
from models import CourseResource, ResourceEvent
import time
import re
import datetime

class SIScraper(BaseScraper):
    def __init__(self, db):
        super().__init__(db, "Supplemental Instruction", "CMU SI Website")
    
    def scrape(self):
        link = "https://www.cmu.edu/student-success/programs/supp-inst.html"
        r = requests.get(link, headers=self.headers)
        soup = bs4.BeautifulSoup(r.text, 'html.parser')

        table = soup.find('table', id="si-table")

        if table is None:
            raise Exception("No table exists on SI website. Could be due to lack of courses (Summer time)")

        resources = []
        for i, row in enumerate(table.find_all('tr')):
            if i != 0:
                data = row.find_all('th') + row.find_all('td')

                course_nameids = data[0].text.strip()
                courses_name_ids_parsed = re.findall(r'(\d{2}-\d{3})\s(.*?)(?=(\d{2}-\d{3})|$)', course_nameids)

                professor = data[1].text.strip()
                si_leader = data[2].text.strip()

                events = []
                for timedata in [t.strip() for t in data[3].contents if "-" in t]:
                    if timedata.startswith("("):
                        continue

                    if " @ " in timedata:
                        weekday, rest = timedata.split(" @ ")
                    else:
                        weekday, rest = timedata.split(" ", 1)
                    
                    weekday = time.strptime(weekday.rstrip("s"), "%A").tm_wday

                    # Calculate the next date for the given weekday
                    next_date = self.get_next_weekday(weekday)

                    data_split = rest.split(" - ")
                    start_time = datetime.datetime.strptime(data_split[0].strip(), "%I:%M%p").time()
                    end_time = datetime.datetime.strptime(data_split[1].strip(), "%I:%M%p").time()

                    # Combine date and time
                    start_datetime = datetime.datetime.combine(next_date, start_time)
                    end_datetime = datetime.datetime.combine(next_date, end_time)

                    location = data_split[2].strip()

                    # Create ResourceEvent
                    event = ResourceEvent(
                        start_datetime=start_datetime,
                        end_datetime=end_datetime,
                        location=location.strip(),
                        recurrence=None  # No recurrence
                    )
                    events.append(event)

                if not events:
                    continue
                
                for course in courses_name_ids_parsed:
                    course_id = course[0]
                    course_name = course[1].strip()
                    resource = CourseResource(
                        resource_type="Supplemental Instruction",
                        resource_source=self.resource_source,
                        course_id=course_id,
                        course_name=course_name,
                        professor=professor if professor else None,
                        instructor=si_leader if si_leader else None,
                        events=events
                    )
                    resources.append(resource)
        
        # Update the database
        unique_keys = ["resource_type", "course_id", "instructor"]
        self.update_database(resources, "academic_events", unique_keys)
    