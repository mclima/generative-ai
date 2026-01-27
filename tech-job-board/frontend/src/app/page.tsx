import { Suspense } from 'react'
import HomePageClient from './HomePageClient'

export default function Home() {
  return (
    <Suspense fallback={null}>
      <HomePageClient />
    </Suspense>
  )
}
