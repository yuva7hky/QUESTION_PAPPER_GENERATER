/**
 * ExamTypeSelector Component
 * 
 * Displays three radio button options:
 *   - CIE – I (CIE_I)
 *   - CIE – II (CIE_II)
 *   - Model Examination (MODEL)
 * 
 * Props:
 *   examType   — current selected value ('CIE_I' | 'CIE_II' | 'MODEL')
 *   onChange   — callback(newValue) when selection changes
 *   disabled   — disables interaction when generating
 */
export default function ExamTypeSelector({ examType, onChange, disabled }) {
  const options = [
    { id: 'exam-type-cie-1', value: 'CIE_I', label: 'CIE – I' },
    { id: 'exam-type-cie-2', value: 'CIE_II', label: 'CIE – II' },
    { id: 'exam-type-model', value: 'MODEL', label: 'Model Examination' },
  ];

  return (
    <div>
      <label className="block text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">
        Select Examination Type
      </label>
      <div className="space-y-2">
        {options.map((opt) => {
          const isSelected = examType === opt.value;
          return (
            <label
              key={opt.value}
              htmlFor={opt.id}
              className={`flex items-center gap-3 p-3 rounded-lg border text-sm font-medium cursor-pointer transition ${
                isSelected
                  ? 'border-indigo-600 bg-indigo-50/50 text-indigo-900 font-semibold shadow-xs'
                  : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300 hover:bg-gray-50/50'
              } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <input
                type="radio"
                id={opt.id}
                name="examType"
                value={opt.value}
                checked={isSelected}
                onChange={() => onChange(opt.value)}
                disabled={disabled}
                className="w-4 h-4 text-indigo-600 border-gray-300 focus:ring-indigo-500 cursor-pointer disabled:cursor-not-allowed"
              />
              <span>{opt.label}</span>
            </label>
          );
        })}
      </div>
    </div>
  );
}
