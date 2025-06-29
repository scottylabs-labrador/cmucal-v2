"use client";
// components/Modal.tsx
import { ReactNode, useState, useEffect } from "react";

import axios from 'axios';
import { useUser } from "@clerk/nextjs";

type ModalProps = {
  showCalendarsModal: boolean;
  setShowCalendarsModal: React.Dispatch<React.SetStateAction<boolean>>; 
  showUploadModal: boolean;
  setShowUploadModal: React.Dispatch<React.SetStateAction<boolean>>;
  onClose: () => void;
  userId: string; 
};

export default function ModalCalendars({ showCalendarsModal, setShowCalendarsModal, 
                                        showUploadModal, setShowUploadModal, onClose, userId }: ModalProps) {
  
  // const { user } = useUser();  // clerk user object
  // if (!user) {
  //   console.error("User not found. Ensure Clerk is properly configured.");
  //   return null; // or handle the case where user is not available
  // }
  // const clerkId = user.id;    // Clerk ID

  // const getUserIdFromClerkId = async (clerkId: string) => {
  //   try {
  //     const res = await axios.get("http://localhost:5001/api/users/get_user_id", {
  //       params: { clerk_id: clerkId },
  //       withCredentials: true,
  //     });
  //     return res.data.user_id;
  //   } catch (err) {
  //     console.error("Failed to fetch user ID:", err);
  //     return null;
  //   }
  // };

  if (!showCalendarsModal || !userId) return null;      
  const [adminCategories, setAdminCategories] = useState<any[]>([]);                                   

  useEffect(() => {
    const fetchAdminCategories = async (userId: string) => {
      try {
        const response = await axios.get('http://localhost:5001/api/users/get_admin_categories', {
          params: { user_id: userId },
          withCredentials: true, // include cookies
        });

        console.log("Admin Categories:", response.data);
        return response.data;
      } catch (error) {
        console.error("Error fetching admin categories:", error);
        return [];
      }
    };

    if (userId) {
      fetchAdminCategories(userId).then(categories => {
        setAdminCategories(categories);
        // console.log("Fetched admin categories:", categories);
      });
    }
  }, [userId]);
  

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-40 z-40"
        onClick={onClose}
      />
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
        <select className="w-full border rounded-md p-2 mb-4">
          {adminCategories.map((category) => (
            <option key={category.id} value={category.id}>{category.organization_name} — {category.name}</option> 
          ))}

        </select>
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded-md w-full"
          onClick={() => {
            setShowCalendarsModal(false);
            setShowUploadModal(true);
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
    </>
  );
}
