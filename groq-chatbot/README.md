# AI Chatbot - Powered by Groq

A general-purpose AI chatbot that leverages Groq's ultra-fast inference platform to deliver real-time responses from Meta's Llama 4 Scout model. Features include:

Conversational memory within sessions
Modern, responsive UI
Server-side API route for secure API key handling
Zero-cost deployment on Vercel

## Features

- ⚡ Lightning-fast responses using Groq's inference engine
- 💬 Conversation history with context
- 🎨 Modern, responsive UI with Tailwind CSS
- 🚀 Ready for Vercel deployment

## Getting Started

### Prerequisites

- Node.js 18+ installed
- Groq API key (get one free at [console.groq.com](https://console.groq.com))

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Set up your environment variables:
   - Open `.env.local`
   - Replace `your_groq_api_key_here` with your actual Groq API key

3. Run the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Deployment to Vercel

1. Push this project to a GitHub repository

2. Go to [vercel.com](https://vercel.com) and sign in with GitHub

3. Click "New Project" and import your repository

4. Add your environment variable:
   - Name: `GROQ_API_KEY`
   - Value: Your Groq API key

5. Click "Deploy"

Your chatbot will be live in about 1 minute!

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **AI**: Groq API with Llama 4 Scout
- **Styling**: Tailwind CSS
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

## URL
https://groq-chatbot-eta.vercel.app/
