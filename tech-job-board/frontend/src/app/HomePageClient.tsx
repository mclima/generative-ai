'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import JobListItem from '@/components/JobListItem'
import JobDetails from '@/components/JobDetails'
import CategoryTabs from '@/components/CategoryTabs'
import SortDropdown from '@/components/SortDropdown'
import Footer from '@/components/Footer'
import { getJobs, refreshJobs, getLastRefresh } from '@/lib/api'
import { Job } from '@/types'
import { Briefcase, Loader2, RefreshCw, Clock, X } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

export default function HomePageClient() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [countdown, setCountdown] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null)
  const [selectedJob, setSelectedJob] = useState<Job | null>(null)
  const [showMobileDetails, setShowMobileDetails] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState(() => {
    return searchParams.get('category') || 'All Jobs'
  })
  const [sortBy, setSortBy] = useState('newest')

  useEffect(() => {
    const categoryFromUrl = searchParams.get('category')
    if (categoryFromUrl && categoryFromUrl !== selectedCategory) {
      setSelectedCategory(categoryFromUrl)
    }
  }, [searchParams])

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category)
    const params = new URLSearchParams(searchParams.toString())
    params.set('category', category)
    router.push(`/?${params.toString()}`)
  }

  useEffect(() => {
    setSelectedJob(null)
    fetchJobs()
    fetchLastRefresh()
  }, [selectedCategory, sortBy])

  useEffect(() => {
    if (jobs.length > 0) {
      setSelectedJob(jobs[0])
    }
  }, [jobs])

  const fetchLastRefresh = async () => {
    try {
      const data = await getLastRefresh()
      if (data.last_refresh) {
        setLastRefresh(new Date(data.last_refresh))
      }
    } catch (err) {
      console.error('Error fetching last refresh:', err)
    }
  }

  useEffect(() => {
    let interval: NodeJS.Timeout
    if (refreshing && countdown > 0) {
      interval = setInterval(() => {
        setCountdown((prev) => Math.max(0, prev - 1))
      }, 1000)
    }
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [refreshing, countdown])

  const fetchJobs = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getJobs(selectedCategory, sortBy)
      console.log('Jobs fetched:', data.length, 'jobs')
      setJobs(data)
    } catch (err) {
      setError('Failed to load jobs. Please try again later.')
      console.error('Error fetching jobs:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleMatchResume = () => {
    router.push('/match-resume')
  }

  const handleRefresh = async () => {
    try {
      setRefreshing(true)
      setCountdown(19)
      setError(null)
      await refreshJobs()
      await fetchJobs()
      await fetchLastRefresh()
    } catch (err) {
      console.error('Error refreshing jobs:', err)
      setError('Failed to refresh jobs. Please try again.')
    } finally {
      setRefreshing(false)
      setCountdown(0)
    }
  }

  const handleJobSelect = (job: Job) => {
    setSelectedJob(job)
    setShowMobileDetails(true)
  }

  const handleCloseMobileDetails = () => {
    setShowMobileDetails(false)
  }

  return (
    <div className="flex flex-col min-h-screen">
      <div className="container mx-auto px-4 pt-6 px-6">
        <div className="mb-6">
          <h1 className="text-3xl md:text-4xl font-bold mb-3">Remote Tech Jobs in the US</h1>
          <p className="text-gray-400 text-base md:text-lg mb-4">
            Discover the latest remote opportunities in AI and Engineering
          </p>
          <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-3 mb-4">
            <p className="text-blue-300 text-sm">
              ℹ️ Showing jobs posted within the last 10 days
            </p>
          </div>
          {lastRefresh && (
            <div className="mt-2 flex items-center gap-2 text-sm text-gray-500">
              <Clock size={16} />
              <span>
                {jobs.length} {jobs.length === 1 ? 'job' : 'jobs'} last refreshed {formatDistanceToNow(lastRefresh, { addSuffix: true })}
              </span>
            </div>
          )}
        </div>

        <div className="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="flex gap-2 items-center flex-wrap">
            <CategoryTabs
              selectedCategory={selectedCategory}
              onSelectCategory={handleCategoryChange}
            />
            <div className="w-4"></div>
            <SortDropdown value={sortBy} onChange={setSortBy} />
            <div className="w-4"></div>
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed text-sm h-[48px]"
              aria-label="Refresh job listings"
            >
              <RefreshCw size={18} className={refreshing ? 'animate-spin' : ''} />
              {refreshing ? 'Refreshing...' : 'Refresh Jobs'}
            </button>
          </div>
          <button
            onClick={handleMatchResume}
            className="bg-primary hover:bg-blue-600 text-white px-4 py-2 rounded-lg font-semibold transition-colors flex items-center gap-2 text-sm"
            aria-label="Match your resume to jobs"
          >
            <Briefcase size={18} />
            Match Resume
          </button>
        </div>
      </div>

      {(loading || refreshing) ? (
        <div className="flex flex-col justify-center items-center py-20">
          <div className="flex items-center">
            <Loader2 className="animate-spin" size={48} />
            {refreshing && countdown > 0 && (
              <p className="ml-3 text-gray-400 text-xl font-semibold">{countdown}s</p>
            )}
          </div>
          {refreshing && <p className="mt-3 text-gray-400">Fetching jobs from APIs...</p>}
        </div>
      ) : error ? (
        <div className="text-center py-20">
          <p className="text-red-400 text-lg">{error}</p>
          <button
            onClick={fetchJobs}
            className="mt-4 text-primary hover:underline"
          >
            Try again
          </button>
        </div>
      ) : jobs.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-gray-400 text-lg">No jobs found in this category.</p>
        </div>
      ) : (
        <>
          <div className="flex-1 overflow-hidden flex flex-col">
            <div className="flex-1 overflow-hidden flex">
              <div className="w-full lg:w-2/5 xl:w-1/3 border-r border-gray-800 overflow-y-auto bg-black">
                <div className="w-full pb-4">
                  {jobs.map((job) => (
                    <JobListItem
                      key={job.id}
                      job={job}
                      isSelected={selectedJob?.id === job.id}
                      onClick={() => handleJobSelect(job)}
                    />
                  ))}
                </div>
              </div>

              <div className="hidden lg:block lg:w-3/5 xl:w-2/3 bg-black overflow-hidden">
                {selectedJob ? (
                  <JobDetails job={selectedJob} />
                ) : (
                  <div className="flex items-center justify-center h-full text-gray-400">
                    <p>Select a job to view details</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {showMobileDetails && selectedJob && (
            <div className="fixed inset-0 bg-black z-50 lg:hidden overflow-y-auto">
              <div className="sticky top-0 bg-gray-900 border-b border-gray-800 p-4 flex items-center justify-between">
                <h2 className="text-lg font-semibold">Job Details</h2>
                <button
                  onClick={handleCloseMobileDetails}
                  className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
                  aria-label="Close job details"
                >
                  <X size={24} />
                </button>
              </div>
              <JobDetails job={selectedJob} />
            </div>
          )}
        </>
      )}

      <div className="mt-auto">
        <Footer />
      </div>
    </div>
  )
}
