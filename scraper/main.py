
from pymongo import MongoClient
import time
import os
import configparser
import traceback

from monitors.academic import SIScraper
from monitors.academic import DropInScraper
from monitors.academic import OfficeHoursScraper
from monitors.academic import PeerTutoringScraper

from monitors.career_club import HandshakeScraper
from monitors.career_club import TartanConnectScraper

try:
    # Read Mongo DB config from config.ini
    config = configparser.ConfigParser()
    config.read(os.path.abspath(os.path.join("config.ini")))
    mongo_url = config['PROD']['DB_URI_SHORT']
except:
    try:
        # Try reading Mongo URL from Environmental Variables
        mongo_url = os.environ["MONGO_URI"]
    except KeyError:
        print("Error: no database info -- put in config.ini or MONGO_URI env variable.")
        exit()

class ScraperBot:
    def __init__(self):
        self.client = MongoClient(mongo_url)
        self.db = self.client.CMUCal
    
    def create_indexes(self):
        print("Creating indexes...")
        academic_collection = self.db["academic_events"]
        career_club_collection = self.db["career_club_events"]

        academic_indexes = ["resource_type", "resource_source", "course_name", "course_id", "events.date"]
        other_indexes = ["resource_type", "resource_source", "event_name", "categories", "events.date"]

        # Create indexes
        for key in academic_indexes:
            academic_collection.create_index(key)
        
        for key in other_indexes:
            career_club_collection.create_index(key)

    def run(self):
        print("Starting scraping cycle...")
        # Initialize scrapers
        academic_scrapers = [
            SIScraper(self.db),
            DropInScraper(self.db),
            OfficeHoursScraper(self.db),
            #PeerTutoringScraper(self.db)
        ]

        career_club_scrapers = [
            #HandshakeScraper(self.db),
            TartanConnectScraper(self.db)
        ]
        scrapers = academic_scrapers + career_club_scrapers

        while True:
            for scraper in scrapers:
                try:
                    print(f"Running {str(scraper)} scraper...")
                    scraper.scrape()
                except Exception as e:
                    print(f"Error running {str(scraper)} scraper:")
                    traceback.print_exc()
            
            print("Waiting 10 minutes for the next cycle...")
            time.sleep(600)

if __name__ == "__main__":
    bot = ScraperBot()
    bot.create_indexes()
    bot.run()
