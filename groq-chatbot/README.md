# AI Chatbot - Powered by Groq

A general-purpose AI chatbot that leverages Groq's ultra-fast inference platform to deliver real-time responses from Meta's Llama 4 Scout model with short-term conversational memory. Features include:

Conversational memory within sessions
Modern, responsive UI
Server-side API route for secure API key handling
Zero-cost deployment on Vercel

## Features

- ⚡ Lightning-fast responses using Groq's inference engine
- 🧠 Short-term memory to maintain conversation context
- 🔍 Real-time web search for current events and up-to-date information
- 💬 Conversation history within sessions
- 🎨 Modern, responsive UI with Tailwind CSS
- 🚀 Ready for Vercel deployment

## Getting Started

### Prerequisites

- Node.js 18+ installed
- Groq API key (get one free at [console.groq.com](https://console.groq.com))
- Serper API key for web search (get one free at [serper.dev](https://serper.dev) - 100 searches/month)

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create a `.env.local` file in the project root and add your API keys:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   SERPER_API_KEY=your_serper_api_key_here
   ```
   Note: `SERPER_API_KEY` is optional but required for web search functionality

3. Run the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Deployment to Vercel

1. Push this project to a GitHub repository

2. Go to [vercel.com](https://vercel.com) and sign in with GitHub

3. Click "New Project" and import your repository

4. Add your environment variables:
   - Name: `GROQ_API_KEY`, Value: Your Groq API key
   - Name: `SERPER_API_KEY`, Value: Your Serper API key

5. Click "Deploy"

Your chatbot will be live in about 1 minute!

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **AI**: Groq API with Llama 4 Scout
- **Web Search**: Serper API
- **Styling**: Tailwind CSS
- **Icons**: React Icons
- **Language**: TypeScript

## Cost

- **Groq API**: Free tier (14,400 requests/day)
- **Vercel Hosting**: Free tier

Total cost: **$0/month** for portfolio use

## Skills Demonstrated
LLM Integration — Groq API, Llama 4 Scout
Frontend — React, Next.js 14, Tailwind CSS
Backend — Next.js API Routes
Deployment — Vercel, GitHub

## Live Demo
https://groq-chatbot-eta.vercel.app/
