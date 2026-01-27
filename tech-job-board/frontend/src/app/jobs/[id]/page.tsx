import { Suspense } from 'react'
import JobDetailsClientPage from './JobDetailsClientPage'

export default function JobDetailsPage() {
  return (
    <Suspense fallback={null}>
      <JobDetailsClientPage />
    </Suspense>
  )
}
