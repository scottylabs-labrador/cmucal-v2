import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";

export default async function Home() {
  const { userId } = await auth();

  if (userId) {
    redirect("/profile"); // redirect to profile if signed in
  }

  return (
    <div className="flex justify-center items-center h-[80vh]">
      {/* Optional: a signed-out landing page or leave empty */}
      <p>Welcome! Please sign in to continue.</p>
    </div>
  );
}