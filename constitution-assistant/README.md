# Constitution Assistant

AI-powered conversational chatbot that answers questions about the constitution using RAG (Retrieval-Augmented Generation). Built with Next.js and LangChain, featuring conversation memory and an accessible, responsive interface.

## Features

- **RAG Framework** - Retrieval-Augmented Generation using LangChain and MemoryVectorStore
- **PDF Processing** - Automatically processes constitution.pdf for question answering
- **Conversation Memory** - Remembers chat history for context-aware follow-up questions
- **Clear Button** - Reset conversation anytime to start fresh
- **Example Questions** - 4 starter questions to help users get started
- **Accessible Design** - Black background with white text, high contrast, ARIA labels
- **Responsive Layout** - Works seamlessly on desktop, tablet, and mobile
- **Optimized Performance** - Next.js with prerendered HTML
- **Vercel Ready** - Configured for one-click deployment

## Technology Stack

- **Next.js 14** - React framework with App Router
- **LangChain** - RAG implementation and document processing
- **OpenAI GPT-4o-mini** - Language model for responses
- **MemoryVectorStore** - Vector database for document embeddings
- **Tailwind CSS** - Utility-first CSS framework
- **pdf-parse** - PDF text extraction

## Setup

### Prerequisites

- Node.js 18+ 
- OpenAI API key

### Installation

1. **Install dependencies:**
```bash
npm install
```

2. **Create environment file:**
```bash
cp .env.example .env
```

3. **Add your OpenAI API key to `.env`:**
```
OPENAI_API_KEY=your_openai_api_key_here
```

4. **Run the development server:**
```bash
npm run dev
```

5. **Open your browser:**
Navigate to [http://localhost:3000](http://localhost:3000)

## Usage

1. **Ask Questions** - Type your question about the constitution in the input field
2. **Use Examples** - Click any example question to get started quickly
3. **Follow-up Questions** - The chatbot remembers your conversation, so you can ask follow-ups
4. **Clear Conversation** - Click the "Clear" button in the header to start a new conversation

## Deployment to Vercel

1. **Push to GitHub:**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin your-repo-url
git push -u origin main
```

2. **Import to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository

3. **Configure Environment Variables:**
   - In Vercel project settings, add:
   - `OPENAI_API_KEY` = your OpenAI API key

4. **Deploy:**
   - Vercel will automatically deploy your app
   - Your app will be live at `your-project.vercel.app`

## Project Structure

```
constitution-assistant/
├── app/
│   ├── api/
│   │   └── chat/
│   │       └── route.js       # RAG API endpoint
│   ├── globals.css            # Global styles
│   ├── layout.js              # Root layout
│   └── page.js                # Main chat interface
├── public/
│   └── constitution.pdf       # Source document
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── next.config.js             # Next.js configuration
├── package.json               # Dependencies
├── postcss.config.js          # PostCSS configuration
├── tailwind.config.js         # Tailwind CSS configuration
└── README.md                  # This file
```

## How It Works

1. **Document Processing** - The constitution.pdf is loaded and split into chunks using LangChain's PDFLoader and RecursiveCharacterTextSplitter
2. **Embeddings** - Text chunks are converted to vector embeddings using OpenAI's embedding model
3. **Vector Storage** - Embeddings are stored in MemoryVectorStore for fast similarity search
4. **Query Processing** - User questions are embedded and matched against stored document chunks
5. **Context Retrieval** - Top 4 most relevant chunks are retrieved
6. **Response Generation** - GPT-4o-mini generates answers using retrieved context and conversation history
7. **Memory** - Full conversation history is maintained for context-aware responses

## Customization

### Change the PDF Document

Replace `public/constitution.pdf` with your own PDF document. The application will automatically process it.

### Adjust Chunk Size

In `app/api/chat/route.js`, modify the text splitter parameters:
```javascript
const textSplitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,      // Adjust chunk size
  chunkOverlap: 200,    // Adjust overlap
});
```

### Modify Example Questions

In `app/page.js`, update the `exampleQuestions` array:
```javascript
const exampleQuestions = [
  "Your custom question 1",
  "Your custom question 2",
  // Add more...
];
```

### Change AI Model

In `app/api/chat/route.js`, modify the model name:
```javascript
const llm = new ChatOpenAI({
  modelName: 'gpt-4o-mini',  // Change to 'gpt-4', 'gpt-3.5-turbo', etc.
  temperature: 0.3,
  openAIApiKey: apiKey,
});
```

## Troubleshooting

**Issue: API returns 404**
- Ensure the dev server is running
- Check that `.env` file exists with valid `OPENAI_API_KEY`

**Issue: PDF not loading**
- Verify `constitution.pdf` exists in the `public/` directory
- Check file permissions

**Issue: Slow responses**
- First request initializes the RAG system (takes longer)
- Subsequent requests are faster due to caching

## License

MIT