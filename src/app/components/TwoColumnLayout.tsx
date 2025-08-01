import { ReactNode } from "react";

interface TwoColumnLayoutProps {
  leftContent: ReactNode;
  rightContent: ReactNode;
}

export default function TwoColumnLayout({ leftContent, rightContent }: TwoColumnLayoutProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-4 w-screen">
      {/* Left Section - Takes 1/3 width on large screens */}
      <aside className="md:col-span-1 p-2 bg-white rounded-lg shadow-md dark:bg-gray-700 overflow-y-auto">
        {leftContent}
      </aside>

      {/* Right Section - Takes 2/3 width on large screens */}
      <main className="md:col-span-2 p-2 bg-white rounded-lg shadow-md dark:bg-gray-700">
        {rightContent}
      </main>
    </div>
  );
}
