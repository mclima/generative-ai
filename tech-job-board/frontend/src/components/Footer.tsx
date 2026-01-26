import { Mail } from 'lucide-react'

export default function Footer() {
  const currentYear = new Date().getFullYear()
  
  return (
    <footer className="border-t border-gray-800 mt-12">
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-4 text-gray-400 text-sm">
          <span>© {currentYear} maria c. lima</span>
          <span className="hidden sm:inline">|</span>
          <a 
            href="mailto:maria.lima.hub@gmail.com"
            className="flex items-center gap-2 text-primary hover:underline transition-colors"
          >
            <Mail size={16} />
            <span>maria.lima.hub@gmail.com</span>
          </a>
        </div>
      </div>
    </footer>
  )
}
