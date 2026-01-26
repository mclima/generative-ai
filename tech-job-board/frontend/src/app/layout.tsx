import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Header from '@/components/Header'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Tech Job Board - Remote Tech Jobs in the US | AI-Powered Job Matching',
  description: 'Discover remote tech jobs in AI, Frontend, Backend, Full Stack, DevOps, and Engineering. Browse hundreds of opportunities with AI-powered resume matching. Updated daily.',
  keywords: 'remote jobs, tech jobs, AI jobs, frontend jobs, backend jobs, full stack jobs, devops jobs, remote work, software engineer jobs, developer jobs, engineering jobs',
  openGraph: {
    title: 'Tech Job Board - Remote Tech Jobs in the US',
    description: 'Find your next remote tech opportunity with AI-powered job matching',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Tech Job Board - Remote Tech Jobs in the US',
    description: 'Find your next remote tech opportunity with AI-powered job matching',
  },
  robots: {
    index: true,
    follow: true,
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 5,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Header />
        <main className="min-h-screen">
          {children}
        </main>
      </body>
    </html>
  )
}
