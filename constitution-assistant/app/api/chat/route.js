import { NextResponse } from 'next/server';

let ragChain = null;

async function initializeRAG() {
  if (ragChain) return ragChain;

  const { ChatOpenAI, OpenAIEmbeddings } = await import('@langchain/openai');
  const { RecursiveCharacterTextSplitter } = await import('langchain/text_splitter');
  const { MemoryVectorStore } = await import('langchain/vectorstores/memory');
  const { ChatPromptTemplate } = await import('@langchain/core/prompts');
  const { StringOutputParser } = await import('@langchain/core/output_parsers');
  const { RunnableSequence } = await import('@langchain/core/runnables');
  const { PDFLoader } = await import('langchain/document_loaders/fs/pdf');
  const { WebPDFLoader } = await import('langchain/document_loaders/web/pdf');
  const path = await import('path');
  const fs = await import('fs');

  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    throw new Error('OPENAI_API_KEY not configured');
  }

  // Prefer local file from public/ in dev; fall back to a URL in production
  const localPdfPath = path.join(process.cwd(), 'public', 'constitution.pdf');
  const pdfUrl = process.env.PDF_URL; // e.g. https://your-domain.vercel.app/constitution.pdf

  let loader;
  if (fs.existsSync(localPdfPath)) {
    loader = new PDFLoader(localPdfPath);
  } else if (pdfUrl) {
    loader = new WebPDFLoader(pdfUrl);
  } else {
    throw new Error('constitution.pdf not found locally and PDF_URL is not set. Set PDF_URL to your deployed URL, e.g. https://<project>.vercel.app/constitution.pdf');
  }

  const rawDocs = await loader.load();
  
  const textSplitter = new RecursiveCharacterTextSplitter({
    chunkSize: 1000,
    chunkOverlap: 200,
  });

  const docs = await textSplitter.splitDocuments(rawDocs);

  const embeddings = new OpenAIEmbeddings({
    openAIApiKey: apiKey,
  });

  const vectorStore = await MemoryVectorStore.fromDocuments(docs, embeddings);

  const retriever = vectorStore.asRetriever({
    searchType: 'similarity',
    k: 4,
  });

  const llm = new ChatOpenAI({
    modelName: 'gpt-4o-mini',
    temperature: 0.3,
    openAIApiKey: apiKey,
  });

  const promptTemplate = ChatPromptTemplate.fromTemplate(
    `You are an AI assistant that helps people understand the constitution. Provide accurate, clear, and helpful responses based on the official constitution document.

Guidelines:
- Provide accurate information based solely on the context provided
- Be professional, friendly, and concise
- If the answer is not in the context, politely state that you don't have that information
- Use clear language and avoid jargon when possible
- Consider the conversation history when answering follow-up questions

Context from Constitution:
{context}

Conversation History:
{chat_history}

Current Question: {question}

Response:`
  );

  const formatDocs = (docs) => {
    return docs.map((doc) => doc.pageContent).join('\n\n');
  };

  ragChain = RunnableSequence.from([
    {
      context: async (input) => {
        const docs = await retriever.getRelevantDocuments(input.question);
        return formatDocs(docs);
      },
      question: (input) => input.question,
      chat_history: (input) => input.chat_history || 'No previous conversation',
    },
    promptTemplate,
    llm,
    new StringOutputParser(),
  ]);

  return ragChain;
}

export async function POST(request) {
  try {
    const { message, history } = await request.json();

    if (!message || message.trim() === '') {
      return NextResponse.json(
        { error: 'Please enter a question' },
        { status: 400 }
      );
    }

    const chatHistory = history && history.length > 0
      ? history.map(msg => `${msg.role === 'user' ? 'User' : 'Assistant'}: ${msg.content}`).join('\n')
      : 'No previous conversation';

    const chain = await initializeRAG();
    const response = await chain.invoke({ 
      question: message,
      chat_history: chatHistory 
    });

    return NextResponse.json({ response });
  } catch (error) {
    console.error('Error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to process request' },
      { status: 500 }
    );
  }
}
