import { useRef } from "react";

type ModalProps = {
  show: boolean;
  onClose: () => void;
};

export default function ModalUpload({ show, onClose }: ModalProps) {
  const fileInputRef = useRef<HTMLInputElement | null>(null);

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
          className="bg-white dark:bg-gray-900 p-6 rounded-xl shadow-xl max-w-xl w-full relative"
          onClick={(e) => e.stopPropagation()}
        >
          <h2 className="text-xl font-semibold mb-2">
            Upload to CMUCal Events Dashboard
          </h2>
          <p className="text-sm text-gray-500 mb-4">
            Either upload a file or paste your Google Calendar link below
          </p>

          {/* Dropzone */}
          <div
            onClick={() => fileInputRef.current?.click()}
            className="flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-md h-40 cursor-pointer text-center hover:bg-gray-50 dark:hover:bg-gray-800 transition mb-4"
          >
            <img
              src="/placeholder-upload-icon.png" // Use your own placeholder if needed
              alt="upload icon"
              className="w-10 h-10 mb-2"
            />
            <p className="text-gray-600 dark:text-gray-300 text-sm">
              Click to select file or drag and drop it here
            </p>
            <p className="text-xs text-gray-400 mt-1">
              .ICS, JPEG, PNG, and PDF formats
            </p>
            <input
              type="file"
              accept=".ics,.jpeg,.jpg,.png,.pdf"
              className="hidden"
              ref={fileInputRef}
            />
          </div>

          {/* Link Input */}
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
