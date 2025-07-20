import { EventInput } from "@fullcalendar/core";
import dayjs, { Dayjs } from "dayjs";


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

export interface RecurrenceInput {
  frequency: "DAILY" | "WEEKLY" | "MONTHLY" | "YEARLY";
  interval: number;
  selectedDays: number[];     // For weekly recurrence: [0 (Sun) - 6 (Sat)]
  ends: "never" | "on" | "after";
  endDate: Dayjs | null;
  occurrences: number;
  startDatetime: Dayjs;
  eventId: number;
}

export interface RecurrenceOutput {
  dbRecurrence: {
    frequency: string;
    interval: number;
    count: number | null;
    until: string | null;
    event_id: number;
    by_day: string | null;
    by_month: number | null;
    by_month_day: number | null;
    start_datetime: string;
  };
  summary: string;
}

export type RRuleFrequency = "DAILY" | "WEEKLY" | "MONTHLY" | "YEARLY";

export type DBRecurrenceEnds = "never" | "on" | "after";