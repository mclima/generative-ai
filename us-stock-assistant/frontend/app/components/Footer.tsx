export default function Footer() {
  return (
    <footer className="bg-[#111111] border-t border-[#2a2a2a] mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center justify-center gap-3 text-gray-500 text-sm">
          <span>© {new Date().getFullYear()} maria c. lima</span>
          <span>|</span>
          <a href="mailto:maria.lima.hub@gmail.com" className="flex items-center gap-1.5 hover:text-gray-300 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            maria.lima.hub@gmail.com
          </a>
        </div>
      </div>
    </footer>
  );
}
