'use client';

import { useState, useCallback } from 'react';
import { Course } from '../utils/types';
import { debounce } from 'lodash';
import { Search } from 'lucide-react';
import { userCourses } from '../profile/data/mockData';

interface CourseSearchProps {
  onCourseSelect?: (course: Course) => void;
}

export default function CourseSearch({ onCourseSelect }: CourseSearchProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<Course[]>([]);

  const handleSearch = useCallback(
    debounce(async (query: string) => {
      setIsLoading(true);
      try {
        // Simulate API call with timeout
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const filteredCourses = userCourses.filter(course => 
          course.courseId.toLowerCase().includes(query.toLowerCase()) ||
          course.name.toLowerCase().includes(query.toLowerCase())
        );
        
        setSearchResults(filteredCourses);
      } catch (error) {
        console.error('Error searching courses:', error);
        setSearchResults([]);
      } finally {
        setIsLoading(false);
      }
    }, 300),
    []
  );

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    if (query.length >= 2) {
      handleSearch(query);
    } else {
      setSearchResults([]);
    }
  };

  return (
    <div className="w-full">
      <div className="relative flex items-center">
        <Search className="absolute left-3 h-5 w-5 text-gray-400" />
        <input
          type="text"
          value={searchQuery}
          onChange={handleInputChange}
          placeholder="Search for a course..."
          className="w-full pl-10 pr-4 py-2 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
        />
        {isLoading && (
          <div className="absolute right-3">
            <div className="animate-spin h-5 w-5 border-2 border-blue-500 rounded-full border-t-transparent"></div>
          </div>
        )}
      </div>

      {searchResults.length > 0 && (
        <div className="mt-2 bg-white border border-gray-300 rounded-md shadow-lg">
          <ul className="divide-y divide-gray-200">
            {searchResults.map(course => (
              <li
                key={course.id}
                className="p-3 hover:bg-gray-50 cursor-pointer"
                onClick={() => onCourseSelect?.(course)}
              >
                <div className="font-medium">{course.courseId}</div>
                <div className="text-sm text-gray-600">{course.name}</div>
                <div className="text-xs text-gray-500">Section {course.section}</div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {searchQuery.length >= 2 && searchResults.length === 0 && !isLoading && (
        <div className="mt-2 text-sm text-gray-600">
          No courses found matching "{searchQuery}"
        </div>
      )}
    </div>
  );
} 