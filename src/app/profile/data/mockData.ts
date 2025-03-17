import { Event, Course, Club } from "../../utils/types";


// Sample event data based on the provided structure
export const sampleEvent: Event = {
  "_id": {
    "$oid": "66f9ed1fca62f327b3eab539"
  },
  "resource_type": "Drop In Tutoring",
  "instructor": "Colin D. & Jordan H.",
  "course_id": "03-121",
  "course_name": "Modern Biology I",
  "start_datetime": "2025-03-16T20:00:00.000+00:00",
  "end_datetime": "2025-03-16T22:00:00.000+00:00",
  "location": "POS 282",
  "professor": null,
  "resource_source": "CMU Drop In Website"
};


// Mock data for user courses and events
export const userCourses: Course[] = [
  { 
    id: "1", 
    courseId: "15-122", 
    name: "Principles of Imperative Computation",
    section: "P",
    options: [
      { id: "1-1", type: "Lecture and recitation", selected: true },
      { id: "1-2", type: "Office hours", selected: true },
      { id: "1-3", type: "Supplemental instruction sessions", selected: true }
    ] 
  },
  { 
    id: "2", 
    courseId: "15-151", 
    name: "Mathematical Foundations in CS",
    section: "K",
    options: [
      { id: "2-1", type: "Lecture and recitation", selected: true },
      { id: "2-2", type: "Office hours", selected: false },
      { id: "2-3", type: "Supplemental instruction sessions", selected: false }
    ] 
  },
];


export const userClubs: Club[] = [
  { 
    id: "1", 
    name: "ScottyLabs",
    options: [
      { id: "club-1-1", type: "General Body Meetings", selected: false },
      { id: "club-1-2", type: "Design weekly meetings", selected: true },
      { id: "club-1-3", type: "CMUCal meetings", selected: true }
    ] 
  }
];


// Generate mock calendar events
export const mockCalendarEvents = [
  {
    id: "mock-1",
    title: "15-122 OH",
    start: "2025-03-16T14:00:00",
    end: "2025-03-16T15:30:00",
    color: "#f87171"
  },
  {
    id: "mock-2",
    title: "15-151 Lecture",
    start: "2025-03-16T09:00:00",
    end: "2025-03-16T10:20:00",
    color: "#f87171"
  },
  {
    id: "mock-3",
    title: "ScottyLabs Meeting",
    start: "2025-03-16T16:00:00",
    end: "2025-03-16T18:00:00",
    color: "#4ade80"
  },
  {
    id: "mock-4",
    title: "15-122 Lecture",
    start: "2025-03-16T12:00:00",
    end: "2025-03-16T13:20:00",
    color: "#f87171"
  }
]; 