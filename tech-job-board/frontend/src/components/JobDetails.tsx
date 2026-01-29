import { Job } from '@/types'
import { formatDate } from '@/lib/utils'
import { Building2, MapPin, Calendar, DollarSign, Tag, ExternalLink } from 'lucide-react'

interface JobDetailsProps {
  job: Job
}

const formatJobDescription = (description: string): string => {
  if (description.includes('<p>') || description.includes('<br>')) {
    return description
  }
  
  const sections = description
    .replace(/([.!?])\s+([A-Z])/g, '$1</p><p>$2')
    .replace(/(Responsibilities|Qualifications|Requirements|What You'll Do|What We're Looking For|About You|Nice to Have|Preferred|Benefits|Perks|What To Expect|First \d+ Days|One Year Outlook):/gi, '</p><h3>$1:</h3><p>')
  
  return `<p>${sections}</p>`
}

export default function JobDetails({ job }: JobDetailsProps) {
  return (
    <div className="h-full overflow-y-auto px-6">
      <div className="bg-gray-900 rounded-xl border border-gray-800 shadow-xl">
        <div className="p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-4 text-white">{job.title}</h1>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-gray-300">
              <div className="flex items-center gap-3">
                <Building2 size={20} className="text-gray-400" />
                <span className="font-medium">{job.company}</span>
              </div>
              
              <div className="flex items-center gap-3">
                <MapPin size={20} className="text-gray-400" />
                <span>{job.location}</span>
              </div>
              
              <div className="flex items-center gap-3">
                <Calendar size={20} className="text-gray-400" />
                <span>Posted {formatDate(job.posted_date)}</span>
              </div>
              
              {job.salary && (
                <div className="flex items-center gap-3">
                  <DollarSign size={20} className="text-gray-400" />
                  <span>{job.salary}</span>
                </div>
              )}
              
              <div className="flex items-center gap-3">
                <Tag size={20} className="text-gray-400" />
                <span className="bg-primary/20 text-primary px-3 py-1.5 rounded-full text-sm font-medium">
                  {job.category}
                </span>
              </div>
              
              <div className="flex items-center gap-3">
                <ExternalLink size={20} className="text-gray-400" />
                <span className="text-gray-400">Source: {job.source}</span>
              </div>
            </div>
          </div>

          <div className="border-t border-gray-800 pt-6 mb-8">
            <a
              href={job.apply_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 bg-primary hover:bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold transition-colors shadow-lg hover:shadow-xl"
              aria-label={`Apply for ${job.title} at ${job.company}`}
            >
              Apply Now
              <ExternalLink size={20} />
            </a>
          </div>

          <div className="border-t border-gray-800 pt-8">
            <h2 className="text-2xl font-semibold mb-6 text-white">About the job</h2>
            {job.description === "Description will be loaded shortly..." || !job.description || job.description.trim() === "" ? (
              <div className="text-gray-400 italic bg-gray-800/50 p-4 rounded-lg">
                Full job description not available. Please visit the job posting for complete details.
              </div>
            ) : (
              <div 
                className="job-description text-gray-300 leading-relaxed"
                dangerouslySetInnerHTML={{ __html: formatJobDescription(job.description) }}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
