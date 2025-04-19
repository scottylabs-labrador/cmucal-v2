import { useAuth } from "@clerk/nextjs";

const { getToken } = useAuth();

export const syncUser = async () => {
  const token = await getToken();

  const res = await fetch("http://localhost:5001/api/sync-user", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    credentials: "include", // include session cookie if you use sessions
  });

  const data = await res.json();
  console.log("User synced:", data);
};

// type User = {
//   id: string;
//   email: string;
//   firstBame: string;
//   lastName: string;
// };

export const sendUserToBackend = async (user: { id: string; email: string; firstName: string; lastName: string }) => {
  const res = await fetch("http://localhost:5001/api/users/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include", 
    body: JSON.stringify({
      clerk_id: user.id,
      email: user.email,
      first_name: user.firstName,
      last_name: user.lastName,
    }),
  });

  const result = await res.json();
  console.log(result);
};

