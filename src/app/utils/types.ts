import { EventInput } from "@fullcalendar/core";


export interface Event {
  _id: {
    $oid: string;
  };
  resource_type: string;
  instructor: string | null;
  course_id: string;
  course_name: string;
  start_datetime: string;
  end_datetime: string;
  location: string;
  professor: string | null;
  resource_source: string;
}


export interface CourseOption {
  id: string;
  type: string;
  selected: boolean;
}


export interface Course {
  id: string;
  courseId: string;
  name: string;
  section: string;
  options: CourseOption[];
}


export interface ClubOption {
  id: string;
  type: string;
  selected: boolean;
}


export interface Club {
  id: string;
  name: string;
  options: ClubOption[];
}


export interface ToggleItemProps {
  checked: boolean;
  onChange: () => void;
  label: string;
}


export interface AccordionProps {
  title: string;
  subtitle?: string;
  color?: string;
  children: React.ReactNode;
  badge?: string;
}

export interface EventOccurrence {
    id: number;
    title: string;
    description: string | null;
    start_datetime: string;
    end_datetime: string;
    location: string;
    is_all_day: boolean;
    source_url: string | null;
    recurrence: string;
    event_id: number;
    org_id: number;
    category_id: number;
}

export interface Category {
    id: number;
    name: string;
}

export interface Course {
    org_id: number;
    course_num: string;
    course_name: string;
    instructors: string[] | null;
    categories: Category[];
    events: {
        [category_name: string]: EventOccurrence[];
    };
}

export interface Club {
    org_id: number;
    name: string;
    description: string | null;
    categories: Category[];
    events: {
        [category_name: string]: EventOccurrence[];
    };
}
