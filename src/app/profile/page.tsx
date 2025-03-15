"use client"

import TwoColumnLayout from "@components/TwoColumnLayout";
import Calendar from "@components/Calendar";

const userSchedule = [
  { id: "1", title: "15-122 Lecture", time: "Mon/Wed/Fri 10:00AM - 11:00AM" },
  { id: "2", title: "15-151 Recitation", time: "Tue 8:00AM - 8:50AM" },
  { id: "3", title: "Office Hours", time: "Thu 2:00PM - 4:00PM" },
];

function ProfileSidebar() {
  return (
    <div>
      <h2 className="text-lg font-semibold mb-2">Current Schedule</h2>
      <ul className="space-y-2">
        {userSchedule.map((item) => (
          <li key={item.id} className="p-2 bg-gray-100 rounded">
            <p className="font-medium">{item.title}</p>
            <p className="text-sm text-gray-600">{item.time}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function Profile() {

  return <TwoColumnLayout leftContent={<ProfileSidebar />} rightContent={<Calendar />} />;
}
