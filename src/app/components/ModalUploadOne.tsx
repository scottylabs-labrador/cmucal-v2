"use client";
// components/Modal.tsx
import { ReactNode, useState, useEffect } from "react";

import axios from 'axios';
import { useUser } from "@clerk/nextjs";

type ModalProps = {
  showUploadModalOne: boolean;
  setShowUploadModalOne: React.Dispatch<React.SetStateAction<boolean>>; 
  showUploadModalTwo: boolean;
  setShowUploadModalTwo: React.Dispatch<React.SetStateAction<boolean>>;
  setSelectedCategory: React.Dispatch<React.SetStateAction<any>>;
  onClose: () => void;
};

export default function ModalUploadOne({ showUploadModalOne, setShowUploadModalOne, 
                                        showUploadModalTwo, setShowUploadModalTwo, setSelectedCategory, onClose}: ModalProps) {
  
  const [selectedOption, setSelectedOption] = useState<any | null>(null);
  const { user } = useUser();  // clerk user object
  const [adminCategories, setAdminCategories] = useState<any[]>([]); 

  if (!user) return null;

  useEffect(() => {
    const fetchAdminCategories = async () => {
      if (!user?.id) return;

      console.log("Fetching admin categories for Clerk ID:", user.id);

      try {
        const response = await axios.get('http://localhost:5001/api/users/get_admin_categories', {
          params: { clerk_id: user.id },
          withCredentials: true,
        });
        setAdminCategories(response.data);
      } catch (error) {
        console.error("Error fetching admin categories:", error);
      }
    };

    fetchAdminCategories();
  }, [user]);


  if (adminCategories.length === 0) {  
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center">
        {/* Backdrop */}
        <div
          className="fixed inset-0 bg-black bg-opacity-40 z-40"
          onClick={onClose}
        />
        {/* Modal */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg max-w-md w-full">
          <h2 className="text-lg font-semibold mb-4">No Calendars Available</h2>
          <p className="text-gray-600 dark:text-gray-400">
            You do not have permission to manage any calendars.
          </p>
          <button

            onClick={onClose}
          >
            &times;
          </button>
        </div>
      </div>
    );
  }
  

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-40 z-40"
        onClick={onClose}
      >
      
      {/* Modal */}
      <div
        className="fixed inset-0 z-50 flex items-center justify-center"
        onClick={onClose}
      >
        <div
          className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg max-w-md w-full"
          onClick={(e) => e.stopPropagation()}
        >
          <h2 className="text-lg font-semibold mb-4">Choose a calendar</h2>
        <select
          className="w-full border rounded-md p-2 mb-4"
          value={selectedOption?.id ?? ""}
          onChange={(e) => {
            const selected = adminCategories.find((cat) => String(cat.id) === e.target.value);
            setSelectedOption(selected || null);
          }}
        >
          <option value="" disabled>Select a calendar</option>
          {adminCategories.map((category) => (
            <option key={category.id} value={category.id}>
              {category.organization_name} — {category.name}
            </option>
          ))}
        </select>
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded-md w-full"
          disabled={!selectedOption}
          onClick={() => {
            if (selectedOption) {
              setSelectedCategory(selectedOption);
              console.log("Selected category:", selectedOption);
              setShowUploadModalOne(false);
              setShowUploadModalTwo(true);
            }
          }}
        >
          Next
        </button>
          <button
            className="absolute top-2 right-2 text-gray-500 hover:text-gray-800 dark:hover:text-white"
            onClick={onClose}
          >
            &times;
          </button>
        </div>
      </div>
      </div>
    </>
  );
}
