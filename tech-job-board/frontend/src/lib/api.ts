import axios from 'axios'
import { Job, MatchedJob } from '@/types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const getJobs = async (category?: string, sortBy: string = 'newest'): Promise<{
  jobs: Job[]
  isCache: boolean
  cacheTime?: string
}> => {
  const params: any = { sort_by: sortBy }
  if (category && category !== 'All Jobs') {
    params.category = category
  }
  const response = await api.get('/api/jobs', { params })
  
  return {
    jobs: response.data,
    isCache: response.headers['x-data-source'] === 'cache',
    cacheTime: response.headers['x-cache-time']
  }
}

export const getJobById = async (id: string): Promise<Job> => {
  const response = await api.get(`/api/jobs/${id}`)
  return response.data
}

export const matchResume = async (formData: FormData): Promise<MatchedJob[]> => {
  const response = await api.post('/api/match-resume', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 120000,
  })
  return response.data
}

export const matchResumeAsync = async (formData: FormData): Promise<{ task_id: string; status: string }> => {
  const response = await api.post('/api/match-resume-async', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const getTaskStatus = async (taskId: string): Promise<{
  id: string
  status: string
  progress: number
  result: MatchedJob[] | null
  error: string | null
}> => {
  const response = await api.get(`/api/task-status/${taskId}`)
  return response.data
}

export const refreshJobs = async () => {
  const response = await api.post('/api/jobs/refresh')
  return response.data
}

export const getCategories = async () => {
  const response = await api.get('/api/categories')
  return response.data
}

export const getStats = async () => {
  const response = await api.get('/api/stats')
  return response.data
}

export const getLastRefresh = async () => {
  const response = await api.get('/api/last-refresh')
  return response.data
}
