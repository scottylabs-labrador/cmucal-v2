"use client";

import { FiFilter, FiPlusCircle } from "react-icons/fi";
import Accordion from "./Accordion";
import ToggleItem from "./ToggleItem";
import EventCard from "./EventCard";
import { sampleEvent } from "../profile/data/mockData";
import { Course, Club } from "../utils/types";

interface ProfileSidebarProps {
  courses: Course[];
  clubs: Club[];
  onToggleCourse: (courseId: string, optionId: string) => void;
  onToggleClub: (clubId: string, optionId: string) => void;
}

/**
 * ProfileSidebar - Sidebar for the profile page that shows courses, clubs, and upcoming events
 */
const ProfileSidebar: React.FC<ProfileSidebarProps> = ({ 
  courses, 
  clubs, 
  onToggleCourse, 
  onToggleClub 
}) => {
  return (
    <div className="h-full">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">My Schedule</h2>
        <button className="text-blue-600 text-sm flex items-center">
          <FiFilter size={14} className="mr-1" /> Filter
        </button>
      </div>

      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-md font-medium">My Courses</h3>
          <button className="text-blue-600 text-sm flex items-center">
            <FiPlusCircle size={14} className="mr-1" /> Add
          </button>
        </div>

        {courses.map(course => (
          <Accordion 
            key={course.id} 
            title={`${course.courseId} ${course.name}`}
            subtitle={`SECTION ${course.section}`}
            color="bg-red-400"
            badge="Spring 2025"
          >
            {course.options.map(option => (
              <ToggleItem
                key={option.id}
                checked={option.selected}
                onChange={() => onToggleCourse(course.id, option.id)}
                label={option.type}
              />
            ))}
          </Accordion>
        ))}
      </div>

      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-md font-medium">My Clubs</h3>
          <button className="text-blue-600 text-sm flex items-center">
            <FiPlusCircle size={14} className="mr-1" /> Add
          </button>
        </div>

        {clubs.map(club => (
          <Accordion 
            key={club.id} 
            title={club.name}
            color="bg-green-400"
          >
            {club.options.map(option => (
              <ToggleItem
                key={option.id}
                checked={option.selected}
                onChange={() => onToggleClub(club.id, option.id)}
                label={option.type}
              />
            ))}
          </Accordion>
        ))}
      </div>

      <div>
        <h3 className="text-md font-medium mb-2">Upcoming Events</h3>
        <EventCard event={sampleEvent} />
      </div>
    </div>
  );
};

export default ProfileSidebar; 