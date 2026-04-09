# AI Design Generator

Transform your creative ideas into stunning visual designs for Netflix campaigns using AI-powered image generation.

https://image-generator-roan-three.vercel.app/

## Features

- 🎬 Generate bespoke images for banners and posters
- 🎨 Powered by OpenAI gpt-image-1-mini
- ⚡ Built with Next.js 16, React, TypeScript, and Tailwind CSS
- 📱 Responsive design
- 💾 Download generated images

## Getting Started

### Prerequisites

- Node.js 18+ 
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. Install dependencies:

```bash
npm install
```

2. Set up environment variables:

```bash
cp .env.example .env.local
```

3. Add your OpenAI API key to `.env.local`:

```
OPENAI_API_KEY=your_actual_api_key_here
```

4. Run the development server:

```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Deployment to Vercel

1. Push your code to GitHub
2. Import your repository on [Vercel](https://vercel.com)
3. Add the `OPENAI_API_KEY` environment variable in Vercel project settings
4. Deploy!

## Tech Stack

- **Frontend**: React, Next.js 16, Tailwind CSS, TypeScript
- **UI Components**: Lucide React (icons)
- **Backend**: Next.js API Routes
- **AI**: OpenAI gpt-image-1-mini
- **Styling**: Tailwind CSS, PostCSS, Autoprefixer
- **Deployment**: Vercel

## Project Structure

```
image-generator/
├── app/
│   ├── api/
│   │   └── generate/
│   │       └── route.ts    # API endpoint for image generation
│   ├── globals.css         # Global styles with Tailwind
│   ├── layout.tsx          # Root layout
│   └── page.tsx            # Main page component
├── .env.example            # Example environment variables
├── .env.local              # Local environment variables (not committed)
├── next.config.js          # Next.js configuration
├── package.json            # Dependencies
├── tailwind.config.ts      # Tailwind configuration
└── tsconfig.json           # TypeScript configuration
```

## License

MIT

## Example
User asks: "What are the main principles?"
    ↓
1. MemoryVectorStore retrieves relevant constitution chunks
2. Conversation Memory provides chat history (empty on first question)
3. Both are sent to GPT-4o-mini to generate response
    ↓
User asks: "Can you explain the first one?"
    ↓
1. MemoryVectorStore retrieves relevant chunks about "first principle"
2. Conversation Memory provides previous Q&A so AI knows what "first one" means
3. Both are sent to GPT-4o-mini to generate contextual response

MemoryVectorStore = Your knowledge base (the book)
Conversation Memory = Your conversation context (what we've been talking about)
