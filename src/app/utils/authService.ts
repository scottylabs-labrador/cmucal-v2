import { useAuth } from "@clerk/nextjs";


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
      fname: user.firstName,
      lname: user.lastName,
    }),
  });

  const result = await res.json();
  console.log(result);
};

