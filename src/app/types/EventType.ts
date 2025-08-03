export type EventType = {
  id: string;
  title: string;
  start_datetime: string;
  end_datetime: string;
  start?: string;  // For event occurrences
  end?: string;    // For event occurrences
  is_all_day: boolean;
  location: string;
  user_edited?: string;
  org_id: string;
  org?: string;
  category_id: string;
  description?: string; 
  event_type?: string;
  user_saved: boolean;
  user_is_admin?: boolean;
};