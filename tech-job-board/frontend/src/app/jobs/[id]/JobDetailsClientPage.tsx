'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { getJobById } from '@/lib/api'
import { Job } from '@/types'
import { formatDate } from '@/lib/utils'
import Footer from '@/components/Footer'
import { ArrowLeft, Building2, MapPin, Calendar, DollarSign, Tag, ExternalLink, Loader2 } from 'lucide-react'

const formatJobDescription = (description: string): string => {
  if (description.includes('<p>') || description.includes('<br>')) {
    return description
  }

  const sections = description
    .replace(/([.!?])\s+([A-Z])/g, '$1</p><p>$2')
    .replace(
      /(Responsibilities|Qualifications|Requirements|What You'll Do|What We're Looking For|About You|Nice to Have|Preferred|Benefits|Perks|What To Expect|First \d+ Days|One Year Outlook):/gi,
      '</p><h3>$1:</h3><p>'
    )

  return `<p>${sections}</p>`
}

export default function JobDetailsClientPage() {
  const params = useParams()
  const router = useRouter()
  const searchParams = useSearchParams()
  const [job, setJob] = useState<Job | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const category = searchParams.get('category') || 'All Jobs'

  useEffect(() => {
    if (params.id) {
      fetchJob(params.id as string)
    }
  }, [params.id])

  const fetchJob = async (id: string) => {
    try {
      setLoading(true)
      setError(null)
      const data = await getJobById(id)
      setJob(data)
    } catch (err) {
      setError('Failed to load job details. Please try again later.')
      console.error('Error fetching job:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center py-20">
          <Loader2 className="animate-spin" size={48} />
        </div>
      </div>
    )
  }

  if (error || !job) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-20">
          <p className="text-red-400 text-lg">{error || 'Job not found'}</p>
          <button
            onClick={() => router.push('/')}
            className="mt-4 text-primary hover:underline"
          >
            Back to jobs
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <button
        onClick={() => router.push(`/?category=${encodeURIComponent(category)}`)}
        className="flex items-center gap-2 text-primary hover:underline mb-6"
        aria-label="Back to jobs"
      >
        <ArrowLeft size={20} />
        Back to Jobs
      </button>

      <div className="bg-gray-900 rounded-lg p-8 border border-gray-800">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-4">{job.title}</h1>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-gray-300">
            <div className="flex items-center gap-2">
              <Building2 size={20} className="text-gray-400" />
              <span>{job.company}</span>
            </div>

            <div className="flex items-center gap-2">
              <MapPin size={20} className="text-gray-400" />
              <span>{job.location}</span>
            </div>

            <div className="flex items-center gap-2">
              <Calendar size={20} className="text-gray-400" />
              <span>Posted {formatDate(job.created_at)}</span>
            </div>

            {job.salary && (
              <div className="flex items-center gap-2">
                <DollarSign size={20} className="text-gray-400" />
                <span>{job.salary}</span>
              </div>
            )}

            <div className="flex items-center gap-2">
              <Tag size={20} className="text-gray-400" />
              <span className="bg-primary/20 text-primary px-3 py-1 rounded-full text-sm">
                {job.category}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <ExternalLink size={20} className="text-gray-400" />
              <span className="text-gray-400">Source: {job.source}</span>
            </div>
          </div>
        </div>

        <div className="border-t border-gray-800 pt-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">Job Description</h2>
          {job.description === "Description will be loaded shortly..." || !job.description || job.description.trim() === "" ? (
            <div className="text-gray-400 italic bg-gray-800/50 p-4 rounded-lg">
              Full job description not available. Please visit the job posting for complete details.
            </div>
          ) : (
            <div
              className="job-description"
              dangerouslySetInnerHTML={{ __html: formatJobDescription(job.description) }}
            />
          )}
        </div>

        <div className="border-t border-gray-800 pt-6">
          <a
            href={job.apply_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 bg-primary hover:bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold transition-colors"
          >
            Apply Now
            <ExternalLink size={20} />
          </a>
        </div>
      </div>
      <Footer />
    </div>
  )
}
