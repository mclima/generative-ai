import Chat from '@/components/Chat'

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-3xl">
        <h1 className="text-3xl font-bold text-white text-center mb-2">
          AI Chatbot
        </h1>
        <p className="text-gray-400 text-center mb-2">
          Powered by Groq & Llama 4 Scout
        </p>
        <p className="text-gray-500 text-sm text-center mb-6">
  Knowledge cutoff: August 2024 • Web search enabled for current info
</p>
        <Chat />
      </div>
    </main>
  )
}
