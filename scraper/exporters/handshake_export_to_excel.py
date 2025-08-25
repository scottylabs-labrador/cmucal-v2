import os
import sys
import configparser
import pandas as pd
from datetime import datetime
from pymongo import MongoClient

# Add the parent directory to Python path so we can import from monitors
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from monitors.career_club import HandshakeScraper

try:
    # Read Mongo DB config from config.ini
    config = configparser.ConfigParser()
    config.read(os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.ini")))
    mongo_url = config['PROD']['DB_URI_SHORT']
except:
    try:
        # Try reading Mongo URL from Environmental Variables
        mongo_url = os.environ["MONGO_URI"]
    except KeyError:
        print("Error: no database info -- put in config.ini or MONGO_URI env variable.")
        exit()

def scrape_and_export():
    client = MongoClient(mongo_url)
    db = client.CMUCal
    
    # Initialize Handshake scraper
    handshake_scraper = HandshakeScraper(db)
    
    try:
        print("Running Handshake scraper...")
        handshake_scraper.scrape()
    except Exception as e:
        print(f"Error running Handshake scraper: {str(e)}")
    
    # Read Handshake events from MongoDB
    all_events = []
    
    # Read career events from Handshake only
    career_events = db.career_club_events.find({'resource_source': 'Handshake'})
    for resource in career_events:
        for event in resource.get('events', []):
            event_data = {
                'Resource Type': resource.get('resource_type', ''),
                'Source': resource.get('resource_source', ''),
                'Event Name': resource.get('event_name', ''),
                'Event Host': resource.get('event_host', ''),
                'Categories': ', '.join(resource.get('categories', [])),
                'Start Time': event.get('start_datetime', ''),
                'End Time': event.get('end_datetime', ''),
                'Location': event.get('location', ''),
                'Event Link': resource.get('event_link', ''),
                'Registration Start': resource.get('registration_start', ''),
                'Registration End': resource.get('registration_end', ''),
                'Employers': ', '.join(resource.get('employers', [])),
                'Registered': resource.get('registered', False),
                'Registered Attendees': resource.get('registered_attendees_count', 0),
                'Recurrence': str(event.get('recurrence', ''))
            }
            all_events.append(event_data)
            print(f"Added Handshake event: {event_data}")
    
    # Convert to DataFrame and save to Excel
    if all_events:
        df = pd.DataFrame(all_events)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), f'handshake_events_{timestamp}.xlsx')
        df.to_excel(output_file, index=False)
        print(f"\nEvents exported to {output_file}")
        print(f"Total events exported: {len(all_events)}")
    else:
        print("No Handshake events were found to export")

if __name__ == "__main__":
    scrape_and_export() 