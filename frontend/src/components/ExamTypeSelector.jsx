/**
 * ExamTypeSelector Component
 * 
 * Dropdown to select the examination type.
 * Currently supports CIE-I (50 Marks) and Model Examination (100 Marks).
 * 
 * Props:
 *   examType   — current selected value ('CIE_I' | 'MODEL')
 *   onChange   — callback(newValue) when selection changes
 *   disabled   — disables interaction when generating
 */
export default function ExamTypeSelector({ examType, onChange, disabled }) {
  return (
    <div>
      <label
        htmlFor="exam-type-select"
        className="block text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide"
      >
        Select Examination Type
      </label>
      <select
        id="exam-type-select"
        value={examType}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="w-full px-3 py-2.5 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700 focus:outline-none focus:ring-2 focus:ring-primary-300 focus:border-primary-400 transition disabled:opacity-50 disabled:cursor-not-allowed appearance-none"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3E%3Cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3E%3C/svg%3E")`,
          backgroundPosition: 'right 8px center',
          backgroundRepeat: 'no-repeat',
          backgroundSize: '20px',
          paddingRight: '36px',
        }}
      >
        <option value="CIE_I">CIE-I (50 Marks)</option>
        <option value="CIE_II">CIE-II (50 Marks)</option>
        <option value="MODEL">Model Examination (100 Marks)</option>
      </select>
    </div>
  );
}
