"use client";


import { useState } from "react";
import { FiChevronRight } from "react-icons/fi";
import { AccordionProps } from "../utils/types";


/**
 * Accordion - A collapsible component with header and content
 */
const Accordion: React.FC<AccordionProps> = ({ 
  title, 
  subtitle, 
  color = "bg-gray-100", 
  children, 
  badge 
}) => {
  const [isOpen, setIsOpen] = useState(true);


  return (
    <div className="mb-4 border rounded-md overflow-hidden">
      <div 
        className="flex items-center justify-between p-3 cursor-pointer"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center">
          <div className={`w-3 h-3 rounded-full mr-3 ${color}`}></div>
          <div>
            <h3 className="font-medium text-sm">{title}</h3>
            {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
          </div>
        </div>
        <div className="flex items-center">
          {badge && <span className="text-xs bg-gray-100 px-2 py-1 rounded mr-2">{badge}</span>}
          <FiChevronRight 
            className={`transition-transform ${isOpen ? 'rotate-90' : ''}`} 
            size={16}
          />
        </div>
      </div>


      {isOpen && (
        <div className="p-3 border-t">
          {children}
        </div>
      )}
    </div>
  );
};


export default Accordion; 