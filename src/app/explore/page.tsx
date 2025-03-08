import TwoColumnLayout from "@components/TwoColumnLayout";
import Calendar from "@components/Calendar";

const searchResults = [
  { id: "1", title: "TartanHacks Hackathon", date: "Feb 2, 10:00AM - Feb 3, 5:00PM", location: "Rangos Auditorium" },
  { id: "2", title: "CMU AI Conference", date: "March 15, 9:00AM - 4:00PM", location: "Gates 6115" },
];

function SearchResultsSidebar() {
  return (
    <div>
      <h2 className="text-lg font-semibold mb-2">Search Results</h2>
      <ul className="space-y-3">
        {searchResults.map((event) => (
          <li key={event.id} className="p-3 bg-gray-100 rounded">
            <p className="font-medium">{event.title}</p>
            <p className="text-sm text-gray-600">{event.date}</p>
            <p className="text-sm text-gray-500">{event.location}</p>
            <button className="mt-2 px-3 py-1 bg-blue-500 text-white rounded">Add</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function Explore() {
  return <TwoColumnLayout leftContent={<SearchResultsSidebar />} rightContent={<Calendar />} />;
}
