"use client";

import { useState } from "react";
import { FiChevronUp, FiChevronDown } from "react-icons/fi";
import Accordion from "./Accordion";
import ToggleItem from "./ToggleItem";
import { Course, Club } from "../utils/types";

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
  const [toggledCategories, setToggledCategories] = useState<Record<number, boolean>>({});
  const [isCoursesOpen, setIsCoursesOpen] = useState(true);
  const [isClubsOpen, setIsClubsOpen] = useState(true);

  const handleToggle = (categoryId: number) => {
    setToggledCategories(prev => ({...prev, [categoryId]: !prev[categoryId]}));
  };

  return (
    <div className="h-full dark:bg-gray-700 dark:text-gray-200 p-4">
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4 cursor-pointer" onClick={() => setIsCoursesOpen(!isCoursesOpen)}>
          <h3 className="text-gray-600 dark:text-gray-400">My Courses</h3>
          {isCoursesOpen ? <FiChevronUp className="w-5 h-5 text-gray-600" /> : <FiChevronDown className="w-5 h-5 text-gray-600" />}
        </div>

        {isCoursesOpen && courses.map(course => (
          <Accordion 
            key={course.org_id} 
            title={course.course_num}
            subtitle={course.course_name}
            onRemove={() => course.categories.forEach(cat => onRemoveCategory(cat.id))}
            color="red"
          >
            {course.categories.map(category => (
              <ToggleItem
                key={category.id}
                label={category.name}
                checked={toggledCategories[category.id] !== false}
                onChange={() => handleToggle(category.id)}
                color="red"
              />
            ))}
          </Accordion>
        ))}
      </div>

      <div className="mb-6">
        <div className="flex justify-between items-center mb-4 cursor-pointer" onClick={() => setIsClubsOpen(!isClubsOpen)}>
          <h3 className="text-gray-600 dark:text-gray-400">My Clubs</h3>
          {isClubsOpen ? <FiChevronUp className="w-5 h-5 text-gray-600" /> : <FiChevronDown className="w-5 h-5 text-gray-600" />}
        </div>

        {isClubsOpen && clubs.map(club => (
          <Accordion 
            key={club.org_id} 
            title={club.name}
            onRemove={() => club.categories.forEach(cat => onRemoveCategory(cat.id))}
            color="green"
          >
            {club.categories.map(category => (
              <ToggleItem
                key={category.id}
                label={category.name}
                checked={toggledCategories[category.id] !== false}
                onChange={() => handleToggle(category.id)}
                color="green"
              />
            ))}
          </Accordion>
        ))}
      </div>
    </div>
  );
};

export default ProfileSidebar; 