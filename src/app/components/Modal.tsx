// components/Modal.tsx
import { ReactNode } from "react";

type ModalProps = {
  show: boolean;
  onClose: () => void;
  children: ReactNode;
};

export default function Modal({ show, onClose, children }: ModalProps) {
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
          className="bg-white dark:bg-gray-900 p-6 rounded-xl shadow-xl max-w-xl w-full max-h-[92vh] overflow-auto relative border border-gray-300 dark:border-gray-700"
          onClick={(e) => e.stopPropagation()}
        >
          
          {children}
          <button
            className="absolute top-2 right-2 text-gray-500 hover:text-gray-800 dark:hover:text-white"
            onClick={onClose}
          >
            &times;
          </button>
        </div>
      </div>
    </>
  );
}