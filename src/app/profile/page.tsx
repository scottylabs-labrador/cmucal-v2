"use client"
import { useState, useEffect } from "react";
import TwoColumnLayout from "@components/TwoColumnLayout";
import { EventInput } from "@fullcalendar/core";
import ProfileSidebar from "../components/ProfileSidebar";
import CustomCalendar from "../components/CustomCalendar";
import { sampleEvent, mockCalendarEvents, userCourses, userClubs } from "./data/mockData";
import { Course, Club } from "../utils/types";
import { 
  calculateMatchScore, 
  parseEventTitle, 
  shouldShowCourseEvent, 
  shouldShowClubEvent 
} from "../utils/helpers"; 
import { useUser } from "@clerk/nextjs";
import { sendUserToBackend } from "~/utils/authService";

/**
 * Profile page with personalized calendar view
 */
export default function Profile() {
  const [courses, setCourses] = useState<Course[]>(userCourses);
  const [clubs, setClubs] = useState<Club[]>(userClubs);
  const [calendarEvents, setCalendarEvents] = useState<EventInput[]>([]);

  const handleCourseSelect = (course: Course) => {
    // Check if course already exists
    if (!courses.some(c => c.courseId === course.courseId)) {
      setCourses(prev => [...prev, {
        ...course,
        options: [
          { id: `${course.id}-1`, type: "Lecture and recitation", selected: true },
          { id: `${course.id}-2`, type: "Office hours", selected: true },
          { id: `${course.id}-3`, type: "Supplemental instruction sessions", selected: true }
        ]
      }]);
    }
  };

  // handle clerk user and sync with backend
  const { user } = useUser();
  useEffect(() => {
    if (user) {
      const emailAddress = user.primaryEmailAddress?.emailAddress ? user.primaryEmailAddress.emailAddress : "";
      const firstName = user.firstName ? user.firstName : "";
      const lastName = user.lastName ? user.lastName : "";
      const userData = {
        id: user.id,
        email: emailAddress,
        firstName: firstName,
        lastName: lastName,
      };
      sendUserToBackend(userData);
    }
  }, [user]);


  // Generic toggle function for options
  const toggleOption = <T extends { id: string, options: { id: string, selected: boolean }[] }>(
    itemId: string,
    optionId: string,
    items: T[],
    setItems: React.Dispatch<React.SetStateAction<T[]>>
  ) => {
    setItems(prevItems => 
      prevItems.map(item => 
        item.id === itemId
          ? {
              ...item,
              options: item.options.map(option => 
                option.id === optionId
                  ? { ...option, selected: !option.selected }
                  : option
              )
            }
          : item
      )
    );
  };

  const toggleCourseOption = (courseId: string, optionId: string) => {
    toggleOption(courseId, optionId, courses, setCourses);
  };

  const toggleClubOption = (clubId: string, optionId: string) => {
    toggleOption(clubId, optionId, clubs, setClubs);
  };

  // Determine if an event should be visible based on user selections
  const shouldShowEvent = (eventId: string, title: string) => {
    // Sample event is always visible
    if (eventId === sampleEvent._id.$oid) return true;

    // Parse the event title
    const { entityId, eventType } = parseEventTitle(title, clubs);

    // Handle course events
    if (entityId) {
      const course = courses.find(c => c.courseId === entityId);
      if (course) return shouldShowCourseEvent(course, eventType);
    }

    // Handle club events
    for (const club of clubs) {
      if (title.includes(club.name)) {
        return shouldShowClubEvent(club, eventType);
      }
    }

    return true; // Default visibility
  };

  // Update displayed events when selections change
  useEffect(() => {
    const allEvents = [
      { 
        id: sampleEvent._id.$oid,
        title: `${sampleEvent.course_id}: ${sampleEvent.resource_type}`, 
        start: sampleEvent.start_datetime,
        end: sampleEvent.end_datetime,
        extendedProps: {
          location: sampleEvent.location,
          instructor: sampleEvent.instructor,
          course_name: sampleEvent.course_name
        },
        color: "#f87171"
      },
      ...mockCalendarEvents
    ];

    setCalendarEvents(
      allEvents.filter(event => shouldShowEvent(event.id as string, event.title as string))
    );
  }, [courses, clubs]);

  return (
    <TwoColumnLayout 
      leftContent={
        <ProfileSidebar 
          courses={courses} 
          clubs={clubs} 
          onToggleCourse={toggleCourseOption} 
          onToggleClub={toggleClubOption}
          onCourseSelect={handleCourseSelect}
        />
      } 
      rightContent={<CustomCalendar events={calendarEvents} />} 
    />
  );
}