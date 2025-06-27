from supabase import create_client
import datetime

class BaseScraper:
    def __init__(self, supabase, monitor_name, resource_source):
        self.supabase = supabase
        self.monitor_name = monitor_name
        self.resource_source = resource_source

    def __str__(self):
        return self.monitor_name

    def scrape(self):
        raise NotImplementedError("Scrape method must be implemented by subclasses.")

    def get_next_weekday(self, weekday):
        today = datetime.datetime.now().date()
        days_ahead = weekday - today.weekday()
        if days_ahead < 0:
            days_ahead += 7
        return today + datetime.timedelta(days=days_ahead)

    def update_database(self, resources, table_name, unique_keys):
        # Fetch current resource IDs from Supabase
        existing_rows = self.supabase.table(table_name)\
            .select(",".join(unique_keys + ['id']))\
            .eq('resource_source', self.resource_source)\
            .execute()
        
        existing_map = {
            tuple(row[key] for key in unique_keys): row['id']
            for row in existing_rows.data
        }

        scraped_keys = set()
        upserts = []

        for resource in resources:
            resource_dict = resource.to_json()
            key_tuple = tuple(resource_dict[key] for key in unique_keys)
            scraped_keys.add(key_tuple)

            if key_tuple in existing_map:
                resource_dict['id'] = existing_map[key_tuple]  # existing entry
            resource_dict['resource_source'] = self.resource_source
            upserts.append(resource_dict)

        # Upsert all records (requires RLS policy or service key)
        self.supabase.table(table_name).upsert(upserts).execute()

        # Delete records that are not in the scraped_keys
        keys_to_delete = [
            existing_map[k] for k in existing_map
            if k not in scraped_keys
        ]
        for row_id in keys_to_delete:
            self.supabase.table(table_name).delete().eq("id", row_id).execute()

        print(f"Upserted: {len(upserts)}, Deleted: {len(keys_to_delete)}")
