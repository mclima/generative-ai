import { formatDistanceToNow } from 'date-fns'

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return formatDistanceToNow(date, { addSuffix: true })
}

export const getMatchColor = (score: number): string => {
  if (score >= 80) return 'text-green-400'
  if (score >= 60) return 'text-orange-400'
  return 'text-gray-400'
}

export const getMatchBgColor = (score: number): string => {
  if (score >= 80) return 'bg-green-900/20 border-green-800'
  if (score >= 60) return 'bg-orange-900/20 border-orange-800'
  return 'bg-gray-900/20 border-gray-800'
}
