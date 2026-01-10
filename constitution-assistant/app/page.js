'use client';

import { useState } from 'react';

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const exampleQuestions = [
    "What are the main principles outlined in the constitution?",
    "What rights are guaranteed to citizens?",
    "How is the government structured?",
    "What is the process for amending the constitution?"
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: input,
          history: messages 
        }),
      });

      const data = await response.json();
      
      if (data.error) {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: `Error: ${data.error}` 
        }]);
      } else {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: data.response 
        }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Failed to get response. Please try again.' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (question) => {
    setInput(question);
  };

  const handleClear = () => {
    setMessages([]);
    setInput('');
  };

  return (
    <main className="min-h-screen bg-black text-white flex flex-col">
      <header className="border-b border-gray-800 p-6">
        <div className="max-w-3xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">Constitution Assistant</h1>
            <p className="text-gray-400 mt-2">Ask questions about the constitution</p>
          </div>
          {messages.length > 0 && (
            <button
              onClick={handleClear}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors border border-gray-700"
              aria-label="Clear conversation"
            >
              Clear
            </button>
          )}
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="max-w-3xl mx-auto space-y-6">
            <div className="text-center space-y-4">
              <h2 className="text-xl font-semibold">Example Questions</h2>
              <div className="grid gap-3">
                {exampleQuestions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => handleExampleClick(question)}
                    className="text-left p-4 bg-gray-900 hover:bg-gray-800 rounded-lg transition-colors border border-gray-800"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`max-w-3xl mx-auto p-4 rounded-lg ${
              message.role === 'user'
                ? 'bg-gray-900 ml-auto'
                : 'bg-gray-800'
            }`}
          >
            <div className="font-semibold mb-2">
              {message.role === 'user' ? 'You' : 'Assistant'}
            </div>
            <div className="whitespace-pre-wrap">{message.content}</div>
          </div>
        ))}

        {loading && (
          <div className="max-w-3xl mx-auto p-4 rounded-lg bg-gray-800">
            <div className="font-semibold mb-2">Assistant</div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        )}
      </div>

      <footer className="border-t border-gray-800 p-6">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about the constitution..."
              className="flex-1 bg-gray-900 text-white px-4 py-3 rounded-lg border border-gray-800 focus:outline-none focus:border-gray-600"
              disabled={loading}
              aria-label="Question input"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-6 py-3 bg-white text-black rounded-lg font-semibold hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              aria-label="Send message"
            >
              Send
            </button>
          </div>
        </form>
        <div className="max-w-3xl mx-auto mt-4 pt-4 border-t border-gray-800">
          <p className="text-sm text-gray-400 text-center flex items-center justify-center gap-2">
            © {new Date().getFullYear()} maria c. lima
            <span>|</span>
            <a 
              href="mailto:maria.lima.hub@gmail.com"
              className="hover:text-white transition-colors flex items-center gap-1"
              aria-label="Email maria.lima.hub@gmail.com"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
              </svg>
              <span>maria.lima.hub@gmail.com</span>
            </a>
          </p>
        </div>
      </footer>
    </main>
  );
}
