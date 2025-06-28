"use client";

import { FiX } from "react-icons/fi";
import Accordion from "./Accordion";
import { Course, Club, Category } from "../utils/types";

interface ProfileSidebarProps {
  courses: Course[];
  clubs: Club[];
  onRemoveCategory: (categoryId: number) => void;
}

const CategoryItem = ({ category, onRemove }: { category: Category, onRemove: (id: number) => void }) => (
    <div className="flex justify-between items-center p-2 bg-gray-100 dark:bg-gray-600 rounded-md mb-2">
        <span>{category.name}</span>
        <button onClick={() => onRemove(category.id)} className="text-red-500 hover:text-red-700" aria-label={`Remove ${category.name}`}>
            <FiX />
        </button>
    </div>
);

/**
 * ProfileSidebar - Sidebar for the profile page that shows courses, clubs, and upcoming events
 */
const ProfileSidebar: React.FC<ProfileSidebarProps> = ({ 
  courses, 
  clubs, 
  onRemoveCategory
}) => {
  return (
    <div className="h-full dark:bg-gray-700 dark:text-gray-200 p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">My Schedule</h2>
      </div>

      <div className="mb-6">
        <div className="mb-2">
          <h3 className="text-md font-medium mb-2">My Courses</h3>
        </div>

        {courses.map(course => (
          <Accordion 
            key={course.org_id} 
            title={`${course.course_num} ${course.course_name}`}
            badge="F24"
          >
            {course.categories.map(category => (
              <CategoryItem key={category.id} category={category} onRemove={onRemoveCategory} />
            ))}
          </Accordion>
        ))}
      </div>

      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-md font-medium">My Clubs</h3>
        </div>

        {clubs.map(club => (
          <Accordion 
            key={club.org_id} 
            title={club.name}
          >
            {club.categories.map(category => (
                <CategoryItem key={category.id} category={category} onRemove={onRemoveCategory} />
            ))}
          </Accordion>
        ))}
      </div>
    </div>
  );
};

export default ProfileSidebar; 