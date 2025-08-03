"use client";

import { useState, useEffect } from "react";
import { FiChevronUp, FiChevronDown, FiEye, FiEdit2 } from "react-icons/fi";
import Link from "next/link";
import axios from "axios";
import { useUser } from "@clerk/nextjs";
import Accordion from "./Accordion";
import ToggleItem from "./ToggleItem";
import SavedEventsList from "./SavedEventsList";
import { Course, Club } from "../utils/types";
import { EventType } from "../types/EventType";

interface ProfileSidebarProps {
  courses: Course[];
  clubs: Club[];
  onRemoveCategory: (categoryId: number) => void;
}

const ProfileSidebar: React.FC<ProfileSidebarProps> = ({ 
  courses, 
  clubs, 
  onRemoveCategory
}) => {
  const { user } = useUser();
  const [toggledCategories, setToggledCategories] = useState<Record<number, boolean>>({});
  const [isCoursesOpen, setIsCoursesOpen] = useState(true);
  const [isClubsOpen, setIsClubsOpen] = useState(true);
  const [isEventsOpen, setIsEventsOpen] = useState(true);
  const [isEditMode, setIsEditMode] = useState(false);
  const [savedEvents, setSavedEvents] = useState<EventType[]>([]);

  useEffect(() => {
    async function fetchSavedEvents() {
      if (!user?.id) return;

      try {
        const response = await axios.get("http://localhost:5001/api/events/user_saved_events", {
          params: { user_id: user.id },
          withCredentials: true,
        });

        // Convert events to match our EventType format
        const events = response.data.map((e: any) => ({
          id: e.id,
          title: e.title,
          start_datetime: e.start,
          end_datetime: e.end,
          location: e.location || "",
          org_id: e.org_id || "",
          category_id: e.category_id || "",
          user_saved: true
        }));

        setSavedEvents(events);
      } catch (error) {
        console.error("Error fetching saved events:", error);
      }
    }

    fetchSavedEvents();
  }, [user?.id]);

  const handleToggle = (categoryId: number) => {
    setToggledCategories(prev => ({...prev, [categoryId]: !prev[categoryId]}));
  };

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
          <Accordion 
            key={course.org_id} 
            title={course.course_num}
            subtitle={course.course_name}
            onRemove={isEditMode ? () => course.categories.forEach(cat => onRemoveCategory(cat.id)) : undefined}
            color="red"
          >
            {course.categories.map(category => (
              <ToggleItem
                key={category.id}
                label={category.name}
                checked={toggledCategories[category.id] !== false}
                onChange={() => handleToggle(category.id)}
                color="red"
                disabled={isEditMode}
              />
            ))}
          </Accordion>
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
          <Accordion 
            key={club.org_id} 
            title={club.name}
            onRemove={isEditMode ? () => club.categories.forEach(cat => onRemoveCategory(cat.id)) : undefined}
            color="green"
          >
            {club.categories.map(category => (
              <ToggleItem
                key={category.id}
                label={category.name}
                checked={toggledCategories[category.id] !== false}
                onChange={() => handleToggle(category.id)}
                color="green"
                disabled={isEditMode}
              />
            ))}
          </Accordion>
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

        {isEventsOpen && (
          <SavedEventsList events={savedEvents} />
        )}
      </div>
    </div>
  );
};

export default ProfileSidebar; 