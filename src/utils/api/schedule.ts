import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

// We can enhance this to automatically include the auth token
// For now, the page component will handle passing the token if needed
// based on how the getSchedule function on the page is implemented.

export const getSchedule = async (userId: string | null | undefined) => {
  if (!userId) {
    throw new Error("User ID is required to fetch schedule.");
  }
  try {
    const response = await api.get('/schedule/', { 
      headers: { 'Clerk-User-Id': userId } 
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching schedule:', error);
    throw error;
  }
};

export const removeCategoryFromSchedule = async (categoryId: number, userId: string | null | undefined) => {
  if (!userId) {
    throw new Error("User ID is required to remove a category.");
  }
  try {
    const response = await api.delete(`/schedule/category/${categoryId}`, { 
      headers: { 'Clerk-User-Id': userId } 
    });
    return response.data;
  } catch (error) {
    console.error(`Error removing category ${categoryId} from schedule:`, error);
    throw error;
  }
}; 