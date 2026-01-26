import { Job } from '@/types'
import { formatDate } from '@/lib/utils'
import { Building2, MapPin, Calendar } from 'lucide-react'

interface JobListItemProps {
  job: Job
  isSelected: boolean
  onClick: () => void
}

export default function JobListItem({ job, isSelected, onClick }: JobListItemProps) {
  return (
    <div className="px-4">
      <button
        onClick={onClick}
        className={`w-full text-left p-3 mb-2 rounded-lg border transition-all ${
          isSelected 
            ? 'bg-gray-900 border-primary shadow-lg shadow-primary/20' 
            : 'bg-gray-900/50 border-gray-800 hover:bg-gray-900 hover:border-gray-700 hover:shadow-md'
        }`}
        aria-label={`View details for ${job.title} at ${job.company}`}
        aria-pressed={isSelected}
      >
      <h3 className={`text-lg font-semibold mb-3 line-clamp-2 ${isSelected ? 'text-primary' : 'text-white'}`}>
        {job.title}
      </h3>
      
      <div className="space-y-2 mb-4">
        <div className="flex items-center gap-2 text-gray-300">
          <Building2 size={16} className="text-gray-400 flex-shrink-0" />
          <span className="text-sm truncate font-medium">{job.company}</span>
        </div>
        
        <div className="flex items-center gap-2 text-gray-300">
          <MapPin size={16} className="text-gray-400 flex-shrink-0" />
          <span className="text-sm truncate">{job.location}</span>
        </div>
        
        <div className="flex items-center gap-2 text-gray-300">
          <Calendar size={16} className="text-gray-400 flex-shrink-0" />
          <span className="text-sm">{formatDate(job.posted_date)}</span>
        </div>
      </div>
      
      <div className="flex items-center justify-between pt-3 border-t border-gray-800">
        <span className="bg-primary/20 text-primary px-3 py-1 rounded-full text-xs font-medium">
          {job.category}
        </span>
        <span className="text-xs text-gray-500">{job.source}</span>
      </div>
    </button>
    </div>
  )
}
