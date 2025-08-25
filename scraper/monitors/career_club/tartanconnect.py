
import requests
from monitors.base_scraper import BaseScraper
from models import OtherResource, ResourceEvent
import datetime

class TartanConnectScraper(BaseScraper):
    def __init__(self, db):
        super().__init__(db, "TartanConnect", "TartanConnect Website")
    
    def scrape(self):
        link = "https://tartanconnect.cmu.edu/mobile_ws/v17/mobile_events_list?range=0&limit=300&filter4_contains=OR&filter4_notcontains=OR&order=undefined&search_word=&&1705612303189"
        s = requests.Session()

        tc_headers = self.headers.copy()

        tc_headers.update({
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://tartanconnect.cmu.edu/events"})
        
        r = s.get(link, headers=tc_headers)

        events = r.text.split('"listingSeparator":null')[1:]

        resources = []
        for event in events:
            name = event.split('"p3":"')[1].split('"')[0]
            host = event.split('"p9":"')[1].split('"')[0]
            categories = event.split('"p22":"')[1].split('"p23')[0].split('List all events filtered by ')[1:]
            categories = [c.split('\\"')[0].replace(" slash ", "/") for c in categories]
            
            loc = event.split('"p6":"')[1].split('"')[0].split('<div')[0]
            if loc == "-":
                location = "N/A"
            elif "Online" in loc:
                location = "Virtual"
            else:
                location = loc
            link = "https://tartanconnect.cmu.edu/rsvp?id=" + event.split('"p1":"')[1].split('"')[0]

            #print(f"{name} | {location} | {link}")

            t = event.split('"p4":"')[1].split('"')[0].strip()
            t = t.replace("<p style='margin:0;'>", " ").replace("</p>", "").replace("&ndash;", "-").strip().split("M - ")
            if "," in t[1]:
                # Multi day event
                start_datetime = datetime.datetime.strptime(t[0].strip() + "M", '%a, %b %d, %Y %I:%M %p')
                end_datetime = datetime.datetime.strptime(t[1].strip(), '%a, %b %d, %Y %I:%M %p')
            else:
                t = t[0] + "M - " + t[1]
                date = " ".join(t.split(" ", 4)[:4])
                times = [st.strip() for st in t.split(" ", 4)[4].split("-")]
                for i in range(2):
                    if ":" not in times[i]:
                        times[i] = times[i].split(' ')[0] + ":00 " + times[i].split(' ')[1]
                start_datetime = datetime.datetime.strptime(date + " " + times[0], '%a, %b %d, %Y %I:%M %p')
                end_datetime = datetime.datetime.strptime(date + " " + times[1], '%a, %b %d, %Y %I:%M %p')
            
            resource_event = ResourceEvent(
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                location=location,
                recurrence=None  # No recurrence
            )

            # Create OtherResource
            resource = OtherResource(
                resource_type="Club",
                resource_source=self.resource_source,
                event_name=name,
                event_host=host,
                events=[resource_event],
                categories=categories
            )
            resources.append(resource)

        # Update the database
        unique_keys = ["resource_type", "resource_source", "event_name", "event_host"]
        self.update_database(resources, "career_club_events", unique_keys)