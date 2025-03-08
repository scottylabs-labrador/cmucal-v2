import { ReactNode } from "react";

interface TwoColumnLayoutProps {
  leftContent: ReactNode;
  rightContent: ReactNode;
}

export default function TwoColumnLayout({ leftContent, rightContent }: TwoColumnLayoutProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-6">
      {/* Left Section - Takes 1/3 width on large screens */}
      <aside className="md:col-span-1 p-4 bg-white rounded-lg shadow-md">
        {leftContent}
      </aside>

      {/* Right Section - Takes 2/3 width on large screens */}
      <main className="md:col-span-2 p-4 bg-white rounded-lg shadow-md">
        {rightContent}
      </main>
    </div>
  );
}
