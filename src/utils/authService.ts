import axios from "axios";
import { useAuth } from "@clerk/nextjs";

export const getUserRole = async (): Promise<string | null> => {
  const { getToken } = useAuth();
  const token = await getToken();

//   if (!token) return null; // Ensure the user is logged in

  try {
    const response = await axios.get("http://127.0.0.1:5001/api/auth/role", {
      headers: { Authorization: `Bearer ${token}` },
    });

    return response.data.role;
  } catch (error) {
    console.error("Error fetching role", error);
    return null;
  }
};
