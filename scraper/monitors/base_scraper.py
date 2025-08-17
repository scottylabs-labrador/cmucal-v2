
from pymongo import UpdateOne
import datetime

class BaseScraper:
    def __init__(self, db, monitor_name, resource_source):
        self.db = db
        self.monitor_name = monitor_name
        self.resource_source = resource_source
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
        }

    def __str__(self):
        return self.monitor_name

    def scrape(self):
        raise NotImplementedError("Scrape method must be implemented by subclasses.")

    def get_next_weekday(self, weekday):
        """
        Given a weekday (0=Monday, 6=Sunday), return the next date with that weekday.
        """
        today = datetime.datetime.now().date()
        days_ahead = weekday - today.weekday()
        if days_ahead < 0:
            days_ahead += 7
        next_date = today + datetime.timedelta(days=days_ahead)
        return next_date

    def update_database(self, resources, collection_name, unique_keys):
        """
        Updates the MongoDB collection with the provided resources.
        All resources must be of the resource_source as the class.

        Parameters:
            resources (list): List of resource objects to be upserted.
            collection_name (str): Name of the MongoDB collection.
            unique_keys (list): List of attribute names that uniquely identify a document.
        """
        # Get the collection from the database
        collection = self.db[collection_name]
        
        # List to store update operations
        operations = []
        
        # Set to track IDs of documents that were scraped
        scraped_ids = set()

        for resource in resources:
            # Create the filter query using the unique keys
            filter_query = {key: getattr(resource, key) for key in unique_keys}
            print(filter_query)
            
            # Document to update (converted to dictionary format)
            update_doc = {"$set": resource.to_json()}
            
            # Add the update operation to the operations list
            operations.append(UpdateOne(filter_query, update_doc, upsert=True))
            
            # Check if this resource already exists in the database, if yes, store its _id
            existing_doc = collection.find_one(filter_query, {"_id": 1})
            if existing_doc:
                scraped_ids.add(existing_doc['_id'])

        if scraped_ids:
            # Find all documents with the specified resource_source and _id not in scraped_ids
            delete_filter = {
                "resource_source": self.resource_source,
                "_id": {"$nin": list(scraped_ids)}
            }
            
            # Delete the documents matching the filter
            delete_result = collection.delete_many(delete_filter)
            if delete_result.deleted_count > 0:
                print(f"Deleted {delete_result.deleted_count} outdated '{self.resource_source}' documents from '{collection_name}'.")
        else:
            print(f"No existing '{self.resource_source}' documents found in '{collection_name}' to delete.")
        
        # Perform bulk write for the update operations (if there are any)
        if operations:
            result = collection.bulk_write(operations)
            print(f"Updated {collection_name} with {self.resource_source} data. Inserted: {result.upserted_count}, Modified: {result.modified_count}")

    def update_database_old(self, resources, collection_name, unique_keys):
        resources_json = [resource.to_json() for resource in resources]

        self.db[collection_name].delete_many({})
        result = self.db[collection_name].insert_many(resources_json)
        print(f"Inserted {len(result.inserted_ids)} {self.resource_source} records into {collection_name} DB.")