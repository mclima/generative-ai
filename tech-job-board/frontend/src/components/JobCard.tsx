import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { Job } from '@/types'
import { formatDate } from '@/lib/utils'
import { Building2, MapPin, Calendar, Tag } from 'lucide-react'

interface JobCardProps {
  job: Job
}

export default function JobCard({ job }: JobCardProps) {
  const searchParams = useSearchParams()
  const category = searchParams.get('category') || 'All Jobs'
  
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 h-full flex flex-col">
      <Link href={`/jobs/${job.id}?category=${encodeURIComponent(category)}`}>
        <h3 className="text-xl font-semibold mb-3 text-primary hover:underline cursor-pointer">
          {job.title}
        </h3>
      </Link>
      
      <div className="space-y-2 mb-4 flex-grow">
        <div className="flex items-center gap-2 text-gray-300">
          <Building2 size={16} className="text-gray-400" />
          <span className="text-sm">{job.company}</span>
        </div>
        
        <div className="flex items-center gap-2 text-gray-300">
          <MapPin size={16} className="text-gray-400" />
          <span className="text-sm">{job.location}</span>
        </div>
        
        <div className="flex items-center gap-2 text-gray-300">
          <Calendar size={16} className="text-gray-400" />
          <span className="text-sm">{formatDate(job.posted_date)}</span>
        </div>
      </div>
      
      <div className="flex items-center justify-between pt-4 border-t border-gray-800">
        <div className="flex items-center gap-2">
          <Tag size={16} className="text-gray-400" />
          <span className="bg-primary/20 text-primary px-3 py-1 rounded-full text-xs font-medium">
            {job.category}
          </span>
        </div>
        <span className="text-xs text-gray-500">{job.source}</span>
      </div>
    </div>
  )
}
