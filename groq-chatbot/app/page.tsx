import Chat from '@/components/Chat';
import { MdEmail } from 'react-icons/md';

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <main className="flex-1 flex flex-col items-center justify-center p-4">
        <div className="w-full max-w-3xl">
          <h1 className="text-3xl font-bold text-white text-center mb-2">
            AI Chat Assistant
          </h1>
          <p className="text-gray-400 text-white text-center mb-2">
            Powered by Groq & Llama 4 Scout with short-term memory.
          </p>
          <p className="text-gray-500 text-white text-sm text-center mb-6">
            Knowledge cutoff: August 2024 • Web search enabled with Serper for current info
          </p>
          <Chat />
        </div>
      </main>
      
      <footer className="py-6 text-center text-white text-sm">
        <p className="flex items-center justify-center gap-2">
          © {new Date().getFullYear()} maria c. lima |
          <a 
            href="mailto:maria.lima.hub@gmail.com"
            className="flex items-center gap-1 hover:text-gray-400 transition-colors"
            aria-label="Email maria.lima.hub@gmail.com"
          >
            <MdEmail size={16} />
            maria.lima.hub@gmail.com
          </a>
        </p>
      </footer>
    </div>
  )
}
