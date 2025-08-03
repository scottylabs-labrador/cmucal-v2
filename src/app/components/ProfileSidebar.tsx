"use client";

import { useState, useEffect } from "react";
import { FiChevronUp, FiChevronDown, FiEye, FiEdit2 } from "react-icons/fi";
import Link from "next/link";
import axios from "axios";
import { useUser } from "@clerk/nextjs";
import { formatDate } from "~/app/utils/dateService";
import { Course, Club, Event } from "../utils/types";

interface ProfileSidebarProps {
  onToggleEvent: (event: Event) => void;
}

const ProfileSidebar: React.FC<ProfileSidebarProps> = ({ onToggleEvent }) => {
  const { user } = useUser();
  const [isCoursesOpen, setIsCoursesOpen] = useState(true);
  const [isClubsOpen, setIsClubsOpen] = useState(true);
  const [isEventsOpen, setIsEventsOpen] = useState(true);
  const [isEditMode, setIsEditMode] = useState(false);
  const [courses, setCourses] = useState<Course[]>([]);
  const [clubs, setClubs] = useState<Club[]>([]);
  const [savedEvents, setSavedEvents] = useState<Event[]>([]);

  useEffect(() => {
    async function fetchSchedule() {
      if (!user?.id) return;

      try {
        const response = await axios.get("http://localhost:5001/api/schedule", {
          params: { user_id: user.id },
          withCredentials: true,
        });

        setCourses(response.data.courses);
        setClubs(response.data.clubs);
        setSavedEvents(response.data.saved_events);
      } catch (error) {
        console.error("Error fetching schedule:", error);
      }
    }

    fetchSchedule();
  }, [user?.id]);

  const ViewEditToggle = ({ isEdit }: { isEdit: boolean }) => (
    <div className="flex gap-2">
      <button 
        className={`p-1 rounded ${!isEdit ? 'bg-gray-100 text-gray-800' : 'text-gray-500'}`}
        onClick={() => setIsEditMode(false)}
      >
        <FiEye className="w-4 h-4" />
      </button>
      <button 
        className={`p-1 rounded ${isEdit ? 'bg-gray-100 text-gray-800' : 'text-gray-500'}`}
        onClick={() => setIsEditMode(true)}
      >
        <FiEdit2 className="w-4 h-4" />
      </button>
    </div>
  );

  const EventItem = ({ event }: { event: Event }) => (
    <div className="flex items-center gap-2 ml-8 mb-2">
      <input
        type="checkbox"
        checked={event.is_saved}
        onChange={() => onToggleEvent(event)}
        className="w-4 h-4 text-blue-600"
      />
      <div>
        <p className="text-sm font-medium">{event.title}</p>
        <p className="text-xs text-gray-500">
          {formatDate(event.start_datetime)} - {formatDate(event.end_datetime)}
        </p>
        {event.location && (
          <p className="text-xs text-gray-500">{event.location}</p>
        )}
      </div>
    </div>
  );

  return (
    <div className="h-full dark:bg-gray-700 dark:text-gray-200 p-4">
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <div className="flex justify-between items-center cursor-pointer" onClick={() => setIsCoursesOpen(!isCoursesOpen)}>
            <h3 className="text-gray-600 dark:text-gray-400 mr-2">
              {isEditMode ? 'Edit Courses' : 'My Courses'}
            </h3>
            {isCoursesOpen ? <FiChevronUp className="w-5 h-5 text-gray-600" /> : <FiChevronDown className="w-5 h-5 text-gray-600" />}
          </div>
          <ViewEditToggle isEdit={isEditMode} />
        </div>

        {isCoursesOpen && courses.map(course => (
          <div key={course.org_id} className="mb-4">
            <h4 className="font-medium mb-2">{course.name}</h4>
            {course.categories.map(category => (
              <div key={category.id} className="mb-4">
                <h5 className="text-sm text-gray-500 mb-2 ml-4">{category.name}</h5>
                {category.events.map(event => (
                  <EventItem key={event.id} event={event} />
                ))}
              </div>
            ))}
          </div>
        ))}
      </div>

      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <div className="flex justify-between items-center cursor-pointer" onClick={() => setIsClubsOpen(!isClubsOpen)}>
            <h3 className="text-gray-600 dark:text-gray-400 mr-2">
              {isEditMode ? 'Edit Clubs' : 'My Clubs'}
            </h3>
            {isClubsOpen ? <FiChevronUp className="w-5 h-5 text-gray-600" /> : <FiChevronDown className="w-5 h-5 text-gray-600" />}
          </div>
          <ViewEditToggle isEdit={isEditMode} />
        </div>

        {isClubsOpen && clubs.map(club => (
          <div key={club.org_id} className="mb-4">
            <h4 className="font-medium mb-2">{club.name}</h4>
            {club.categories.map(category => (
              <div key={category.id} className="mb-4">
                <h5 className="text-sm text-gray-500 mb-2 ml-4">{category.name}</h5>
                {category.events.map(event => (
                  <EventItem key={event.id} event={event} />
                ))}
              </div>
            ))}
          </div>
        ))}
      </div>

      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <div className="flex justify-between items-center cursor-pointer" onClick={() => setIsEventsOpen(!isEventsOpen)}>
            <h3 className="text-gray-600 dark:text-gray-400 mr-2">My Events</h3>
            {isEventsOpen ? <FiChevronUp className="w-5 h-5 text-gray-600" /> : <FiChevronDown className="w-5 h-5 text-gray-600" />}
          </div>
          <Link 
            href="/explore" 
            className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            Explore
          </Link>
        </div>

        {isEventsOpen && savedEvents.map(event => (
          <div key={event.id} className="p-3 rounded border mb-2">
            <p className="text-lg">{event.title}</p>
            <p className="text-base text-gray-500">
              {formatDate(event.start_datetime)} - {formatDate(event.end_datetime)}
            </p>
            {event.location && (
              <p className="text-base text-gray-500">{event.location}</p>
            )}
            <button
              onClick={() => onToggleEvent(event)}
              className="mt-2 px-3 py-1.5 rounded-lg bg-blue-300 text-white"
            >
              Remove
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProfileSidebar; 