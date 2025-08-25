
import requests
from monitors.base_scraper import BaseScraper
from models import OtherResource, ResourceEvent
import datetime
import json
import os

class HandshakeScraper(BaseScraper):
    def __init__(self, db):
        super().__init__(db, "Handshake", "Handshake")
        self.base_url = "https://app.joinhandshake.com"
        self.api_url = f"{self.base_url}/stu/graphql"
        
        # Try to get auth token from environment variable
        self.auth_token = os.environ.get("HANDSHAKE_AUTH_TOKEN")
        if not self.auth_token:
            print("Warning: HANDSHAKE_AUTH_TOKEN not set. Please set it to your Handshake authentication token.")
            print("You can find this by:")
            print("1. Log into Handshake")
            print("2. Open browser developer tools (F12)")
            print("3. Go to Application > Cookies > app.joinhandshake.com")
            print("4. Find the 'hss-global' cookie value")
            return
        
        # Update headers with auth token
        self.headers.update({
            "Cookie": f"hss-global={self.auth_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def scrape(self):
        if not self.auth_token:
            print("Error: Cannot scrape without authentication token")
            return []

        # Load the GraphQL query
        with open("monitor_data/handshake_req.dat", "r") as f:
            payload = json.load(f)
        
        # Update query parameters to match Handshake's requirements
        payload["variables"].update({
            "first": 100,  # Get up to 100 events
            "params": {
                "employers": [],
                "categories": [],
                "medium": "HYBRID",  # Must be one of: VIRTUAL, IN_PERSON, HYBRID
                "sort": "DATE",  # Must be one of: RELEVANCE, DATE
                "date": "NEXT_30",  # Must be one of: TODAY, NEXT_5, NEXT_7, NEXT_10, NEXT_30, PAST_YEAR, ALL
                "collection": "ALL",
                "searchModels": ["Event", "CareerFair", "MeetingSchedule"]
            }
        })

        try:
            # Make the API request
            s = requests.Session()
            r = s.post(self.api_url, json=payload, headers=self.headers)
            r.raise_for_status()  # Raise exception for bad status codes
            
            data = r.json()
            if "errors" in data:
                print("GraphQL Errors:", data["errors"])
                return []
                
            events = data["data"]["eventAbstractions"]["edges"]
            
            resources = []
            for event in events:
                node = event["node"]
                name = node["name"]
                host = node["host"]["name"] if "host" in node else "Unknown Host"
                categories = [c["name"] for c in node.get("categories", [])]
                
                # Get location
                if node.get("medium") == "IN_PERSON":
                    location = "In Person"
                elif node.get("medium") == "VIRTUAL":
                    location = "Virtual"
                else:
                    location = str(node.get("medium", "Unknown"))
                
                # Get event link
                event_id = node["id"]
                event_link = f"{self.base_url}/stu/events/{event_id}"
                
                # Parse dates
                try:
                    start_datetime = datetime.datetime.strptime(node["startDate"], '%Y-%m-%dT%H:%M:%S%z')
                    end_datetime = datetime.datetime.strptime(node["endDate"], '%Y-%m-%dT%H:%M:%S%z')
                except (ValueError, KeyError) as e:
                    print(f"Error parsing dates for event {name}: {e}")
                    continue
                
                # Get registration info
                reg_start = node.get("studentRegistrationStart")
                reg_end = node.get("studentRegistrationEnd")
                if reg_start and reg_end:
                    try:
                        reg_start = datetime.datetime.strptime(reg_start, '%Y-%m-%dT%H:%M:%S%z')
                        reg_end = datetime.datetime.strptime(reg_end, '%Y-%m-%dT%H:%M:%S%z')
                    except ValueError:
                        reg_start = reg_end = None
                
                # Get employer info if available
                employers = []
                if "employers" in node:
                    employers = [emp["name"] for emp in node["employers"]]
                
                # Create event object
                resource_event = ResourceEvent(
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    location=location,
                    recurrence=None
                )
                
                # Create resource object with additional metadata
                resource = OtherResource(
                    resource_type="Career",
                    resource_source=self.resource_source,
                    event_name=name,
                    event_host=host,
                    events=[resource_event],
                    categories=categories,
                    metadata={
                        "event_link": event_link,
                        "registration_start": reg_start.isoformat() if reg_start else None,
                        "registration_end": reg_end.isoformat() if reg_end else None,
                        "employers": employers,
                        "registered": node.get("registered", False),
                        "registered_attendees_count": node.get("registeredAttendeesCount", 0)
                    }
                )
                
                resources.append(resource)
                print(f"Found event: {name} | {location} | {event_link}")
            
            # Update database
            unique_keys = ["resource_type", "resource_source", "event_name", "event_host"]
            self.update_database(resources, "career_club_events", unique_keys)
            
            return resources
            
        except requests.exceptions.RequestException as e:
            print(f"Error making request to Handshake API: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error in Handshake scraper: {e}")
            return []
