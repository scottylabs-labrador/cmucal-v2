import { ToggleItemProps } from "../utils/types";

/**
 * ToggleItem - A checkbox with a label
 */
const ToggleItem: React.FC<ToggleItemProps> = ({ checked, onChange, label }) => {
  return (
    <label className="flex items-center space-x-2 cursor-pointer py-1">
      <input 
        type="checkbox" 
        checked={checked} 
        onChange={onChange}
        className="h-4 w-4 text-blue-500 rounded border-gray-300 focus:ring-blue-500"
      />
      <span className="text-sm">{label}</span>
    </label>
  );
};

export default ToggleItem;