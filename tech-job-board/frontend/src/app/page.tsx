import { Suspense } from 'react'
import HomePageClient from './HomePageClient'

export const dynamic = 'force-dynamic'

export default function Home() {
  return (
    <Suspense fallback={null}>
      <HomePageClient />
    </Suspense>
  )
}
