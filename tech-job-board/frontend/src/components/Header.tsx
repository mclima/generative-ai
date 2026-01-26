import Link from 'next/link'
import { Briefcase } from 'lucide-react'

export default function Header() {
  return (
    <header className="border-b border-gray-800 bg-black">
      <div className="container mx-auto px-4 py-4">
        <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity w-fit">
          <Briefcase size={32} className="text-primary" />
          <h1 className="text-2xl font-bold">Tech Job Board</h1>
        </Link>
      </div>
    </header>
  )
}
