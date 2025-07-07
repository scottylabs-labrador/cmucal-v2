"use client";
import { useRef } from "react";

interface ModalProps {
  show: boolean;
  onClose: () => void;
}

export default function ModalUploadTwo({ show, onClose }: ModalProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  if (!show) return null;

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
          ref={containerRef}
          className="bg-white dark:bg-gray-900 p-6 rounded-xl shadow-xl max-w-xl w-full max-h-[90vh] overflow-auto relative"
          onClick={(e) => e.stopPropagation()}
        >
          <h2 className="text-xl font-semibold mb-4">
            Upload to CMUCal Events Dashboard
          </h2>

          {/* Tags */}
          <div className="flex space-x-2 mb-4">
            {['Academic', 'Career', 'Club'].map((tag) => (
              <button
                key={tag}
                className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300 text-sm"
              >
                {tag}
              </button>
            ))}
          </div>

          {/* Title */}
          <input
            className="w-full border px-3 py-2 mb-3 rounded"
            placeholder="Add event title"
          />

          {/* Host */}
          <select className="w-full border px-3 py-2 mb-3 rounded">
            <option>Select a host</option>
          </select>

          {/* Date & Time */}
          <div className="flex space-x-2 mb-3 items-center">
            <input type="date" className="border px-3 py-2 rounded w-full" />
            <input type="time" className="border px-3 py-2 rounded w-full" />
            <span>-</span>
            <input type="time" className="border px-3 py-2 rounded w-full" />
            <label className="ml-2 text-sm">
              <input type="checkbox" className="mr-1" /> All day
            </label>
          </div>

          {/* Repeats */}
          <select className="w-full border px-3 py-2 mb-3 rounded">
            <option>Does not repeat</option>
          </select>

          {/* Location */}
          <input
            className="w-full border px-3 py-2 mb-3 rounded"
            placeholder="Add location"
          />

          {/* Category */}
          <select className="w-full border px-3 py-2 mb-3 rounded">
            <option>example</option>
          </select>

          {/* Source URL */}
          <input
            className="w-full border px-3 py-2 mb-3 rounded"
            placeholder="Add source URL (optional)"
          />

          {/* Description */}
          <textarea
            className="w-full border px-3 py-2 mb-3 rounded"
            placeholder="Add description"
          />

          {/* Require Registration */}
          <label className="flex items-center space-x-2 mb-3">
            <input type="checkbox" />
            <span>require registration</span>
          </label>

          {/* Google Calendar Link */}
          <input
            type="text"
            placeholder="https://calendar.google.com/"
            className="w-full p-2 border rounded-md mb-2 bg-white dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-1 focus:ring-gray-400 dark:focus:ring-gray-600"
          />

          <p className="text-xs text-gray-400 mb-4">
            Need help? Go to Calendar Settings &gt; Get Sharable Link
          </p>

          {/* Buttons */}
          <div className="flex justify-end">
            <button
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600"
              onClick={onClose}
            >
              Continue
            </button>
          </div>

          {/* Close Button */}
          <button
            onClick={onClose}
            className="absolute top-3 right-3 text-gray-400 hover:text-gray-700 dark:hover:text-white"
          >
            &times;
          </button>
        </div>
      </div>
    </>
  );
}
