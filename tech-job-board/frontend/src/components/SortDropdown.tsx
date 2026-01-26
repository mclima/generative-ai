import { ArrowUpDown } from 'lucide-react'

interface SortDropdownProps {
  value: string
  onChange: (value: string) => void
}

export default function SortDropdown({ value, onChange }: SortDropdownProps) {
  return (
    <div className="relative">
      <ArrowUpDown size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="bg-gray-900 border border-gray-800 text-white pl-10 pr-4 py-3 rounded-lg focus:outline-none focus:border-primary cursor-pointer appearance-none font-semibold text-sm h-[48px]"
        aria-label="Sort jobs"
      >
        <option value="newest">Newest First</option>
        <option value="oldest">Oldest First</option>
      </select>
    </div>
  )
}
