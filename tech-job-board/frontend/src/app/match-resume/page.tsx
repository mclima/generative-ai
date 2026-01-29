'use client'

import { useEffect, useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import { matchResumeAsync, getTaskStatus } from '@/lib/api'
import { MatchedJob } from '@/types'
import MatchedJobCard from '@/components/MatchedJobCard'
import Footer from '@/components/Footer'
import { ArrowLeft, Upload, FileText, Loader2, Info } from 'lucide-react'

export default function MatchResumePage() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<'paste' | 'upload'>('paste')
  const [resumeText, setResumeText] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [matchedJobs, setMatchedJobs] = useState<MatchedJob[]>([])
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [hasSearched, setHasSearched] = useState(false)
  const resultsRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (!hasSearched || loading) return
    resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [hasSearched, loading, matchedJobs.length])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
      
      if (!validTypes.includes(selectedFile.type)) {
        setError('Please upload a PDF, DOCX, or TXT file')
        return
      }
      
      setFile(selectedFile)
      setResumeText('')
      setError(null)
    }
  }

  const pollTaskStatus = async (taskId: string) => {
    const maxAttempts = 60 // Poll for up to 3 minutes (60 * 3s)
    let attempts = 0
    let consecutiveErrors = 0
    const maxConsecutiveErrors = 3

    const poll = async () => {
      try {
        const status = await getTaskStatus(taskId)
        consecutiveErrors = 0 // Reset error count on success
        setProgress(status.progress)

        if (status.status === 'completed' && status.result) {
          setMatchedJobs(status.result)
          setLoading(false)
          return
        }

        if (status.status === 'failed') {
          setError(status.error || 'Failed to match resume. Please try again.')
          setLoading(false)
          return
        }

        attempts++
        if (attempts < maxAttempts) {
          setTimeout(poll, 3000) // Poll every 3 seconds
        } else {
          setError('Processing is taking longer than expected. The server may be under heavy load. Please try again in a few moments.')
          setLoading(false)
        }
      } catch (err: any) {
        consecutiveErrors++
        console.error('Polling error:', err)
        
        // If we hit too many consecutive errors, stop polling
        if (consecutiveErrors >= maxConsecutiveErrors) {
          setError('Network connection lost. Please check your internet connection and try again.')
          setLoading(false)
          return
        }
        
        // Otherwise, retry with exponential backoff
        attempts++
        if (attempts < maxAttempts) {
          const backoffDelay = Math.min(3000 * Math.pow(1.5, consecutiveErrors - 1), 10000)
          setTimeout(poll, backoffDelay)
        } else {
          setError('Unable to complete resume matching due to network issues. Please try again.')
          setLoading(false)
        }
      }
    }

    poll()
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!resumeText && !file) {
      setError('Please provide resume text or upload a file')
      return
    }

    try {
      setLoading(true)
      setProgress(0)
      setError(null)
      setHasSearched(true)
      
      const formData = new FormData()
      if (file) {
        formData.append('resume_file', file)
      } else {
        formData.append('resume_text', resumeText)
      }

      const { task_id } = await matchResumeAsync(formData)
      pollTaskStatus(task_id)
    } catch (err: any) {
      setError(err.message || 'Failed to match resume. Please try again.')
      console.error('Error matching resume:', err)
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <button
        onClick={() => router.push('/')}
        className="flex items-center gap-2 text-primary hover:underline mb-6"
        aria-label="Back to jobs"
      >
        <ArrowLeft size={20} />
        Back to Jobs
      </button>

      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-4">Match Your Resume</h1>
        <p className="text-gray-400 text-lg mb-8">
          Upload your resume or paste the text to find jobs that match your skills and experience
        </p>

        <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-4 mb-4 flex gap-3">
          <Info size={20} className="text-primary flex-shrink-0 mt-0.5" />
          <p className="text-sm text-gray-300">
            <strong>Tip:</strong> For best results, use an ATS-compatible resume format (plain text, clear headings, standard fonts, no complex formatting or graphics).
          </p>
        </div>

        <div className="bg-gradient-to-r from-yellow-900/20 to-orange-900/20 border border-yellow-800/50 rounded-lg p-4 mb-8 flex gap-3">
          <Info size={20} className="text-yellow-500 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-gray-300">
            <strong>AI Insights:</strong> Job matches with 80% or higher scores include personalized AI-generated explanations highlighting aligned skills and growth opportunities.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="bg-gray-900 rounded-lg p-8 border border-gray-800 mb-8">
          {/* Tabs */}
          <div className="flex gap-4 mb-6 border-b border-gray-800">
            <button
              type="button"
              onClick={() => setActiveTab('paste')}
              className={`pb-3 px-4 font-semibold transition-colors ${
                activeTab === 'paste'
                  ? 'text-primary border-b-2 border-primary'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              <div className="flex items-center gap-2">
                <FileText size={20} />
                Paste Text
              </div>
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('upload')}
              className={`pb-3 px-4 font-semibold transition-colors ${
                activeTab === 'upload'
                  ? 'text-primary border-b-2 border-primary'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              <div className="flex items-center gap-2">
                <Upload size={20} />
                Upload File
              </div>
            </button>
          </div>

          {/* Paste Tab Content */}
          {activeTab === 'paste' && (
            <div className="mb-6">
              <label htmlFor="resume-text" className="block text-sm font-semibold mb-2">
                Paste Resume Text
              </label>
              <textarea
                id="resume-text"
                value={resumeText}
                onChange={(e) => {
                  setResumeText(e.target.value)
                  setFile(null)
                }}
                rows={12}
                className="w-full bg-black border border-gray-700 rounded-lg p-4 focus:outline-none focus:border-primary"
                placeholder="Paste your resume text here..."
                disabled={loading}
              />
            </div>
          )}

          {/* Upload Tab Content */}
          {activeTab === 'upload' && (
            <div className="mb-6">
              <label className="block text-sm font-semibold mb-2">
                Upload Resume
              </label>
              <div className="relative">
                <input
                  type="file"
                  onChange={handleFileChange}
                  accept=".pdf,.docx,.txt"
                  className="hidden"
                  id="resume-upload"
                  disabled={loading}
                />
                <label
                  htmlFor="resume-upload"
                  className="flex items-center justify-center gap-2 border-2 border-dashed border-gray-700 hover:border-primary rounded-lg p-8 cursor-pointer transition-colors"
                >
                  <Upload size={24} className="text-gray-400" />
                  <span className="text-gray-400">
                    {file ? file.name : 'Click to upload PDF, DOCX, or TXT'}
                  </span>
                </label>
              </div>
            </div>
          )}

          {error && (
            <div className="mb-6 bg-red-900/20 border border-red-800 rounded-lg p-4 text-red-400">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || (!resumeText && !file)}
            className="w-full bg-primary hover:bg-blue-600 disabled:bg-gray-700 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-semibold transition-colors flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin" size={20} />
                Analyzing Resume... {progress}%
              </>
            ) : (
              <>
                <FileText size={20} />
                Find Matching Jobs
              </>
            )}
          </button>
        </form>

        {hasSearched && !loading && (
          <div ref={resultsRef}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">
                {matchedJobs.length > 0 
                  ? `Found ${matchedJobs.length} Matching Jobs` 
                  : 'No Matching Jobs Found'}
              </h2>
              <button
                onClick={() => {
                  setResumeText('')
                  setFile(null)
                  setMatchedJobs([])
                  setHasSearched(false)
                  setError(null)
                }}
                className="bg-gray-800 hover:bg-gray-700 text-white px-6 py-2 rounded-lg font-semibold transition-colors"
              >
                Match Another Resume
              </button>
            </div>
            
            {matchedJobs.length > 0 ? (
              <div className="grid grid-cols-1 gap-6">
                {matchedJobs.map((job) => (
                  <MatchedJobCard key={job.id} job={job} />
                ))}
              </div>
            ) : (
              <div className="bg-gray-900 rounded-lg p-8 border border-gray-800 text-center">
                <p className="text-gray-400">
                  No jobs matched your resume with a score of 60% or higher. Try updating your resume or check back later for new opportunities.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
      <Footer />
    </div>
  )
}
