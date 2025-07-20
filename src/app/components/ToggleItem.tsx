"use client";

interface ToggleItemProps {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  color?: 'red' | 'green';
}

const ToggleItem: React.FC<ToggleItemProps> = ({ label, checked, onChange, color = 'green' }) => {
  const colorClasses = {
    red: 'border-red-200 checked:border-red-500 checked:bg-red-500',
    green: 'border-green-200 checked:border-green-500 checked:bg-green-500',
  };

  return (
    <label className="flex items-center py-1.5 cursor-pointer">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className={`
          w-[18px] h-[18px]
          rounded
          border-2
          bg-white
          transition-colors
          focus:ring-0
          cursor-pointer
          ${colorClasses[color]}
        `}
      />
      <span className="ml-3 text-[15px] text-gray-900 dark:text-gray-100">{label}</span>
    </label>
  );
};

export default ToggleItem;