from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime
from app.scraper.monitors.base_scraper import BaseScraper
from app.scraper.models_scraper import RecurrenceRule, CareerMeta, AcademicMeta

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)


class TestScraper(BaseScraper):
    def scrape(self):
        pass  # Not needed for this test

scraper = TestScraper(
    supabase=supabase,
    monitor_name="test_monitor",
    resource_source="test_source"
)

# Define some test resources
cm1 = CareerMeta(1, "CMU Career Center",
                "https://careers.cmu.edu/event/123",
                True)
cm2 = CareerMeta(2, "CPDC",
                "https://cmu.joinhandshake.com/stu/career_fairs/56853?ref=events-search",
                True)
cm3 = CareerMeta(3, "IBM",
                "https://cmu.joinhandshake.com/stu/events/1759474?ref=events-search",
                True)

resources = [ cm1, cm2, cm3 ]

# Run the update logic
scraper.update_database(
    resources=resources,
    table_name="Career",
    unique_keys=["event_id"]
)

