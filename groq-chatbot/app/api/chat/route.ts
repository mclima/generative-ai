// app/api/chat/route.ts 
import Groq from 'groq-sdk'
import { NextResponse } from 'next/server'

const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY,
})

async function searchWeb(query: string): Promise<string> {
  if (!process.env.SERPER_API_KEY) {
    return 'Search unavailable: Missing SERPER_API_KEY'
  }

  try {
    const response = await fetch('https://google.serper.dev/search', {
      method: 'POST',
      headers: {
        'X-API-KEY': process.env.SERPER_API_KEY,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ q: query }),
    })

    if (!response.ok) throw new Error('Search failed')

    const data = await response.json()

    // Check if organic results exist
    if (!data.organic || data.organic.length === 0) {
      return 'No search results found for this query.'
    }

    // Format top 5 results cleanly
    return data.organic
      .slice(0, 5)
      .map((result: any, i: number) => 
        `${i + 1}. **${result.title}**\n${result.snippet}\nSource: ${result.link}`
      )
      .join('\n\n')
  } catch (error) {
    console.error('Serper search error:', error)
    return 'Search failed. Please try again or rephrase your question.'
  }
}

const SYSTEM_MESSAGE = {
  role: 'system' as const,
  content: 'You are a helpful, friendly AI assistant. Use the search_web tool ONLY when the question requires information after August 2024 (your knowledge cutoff). If the answer can be given confidently from your training data, respond directly without searching.',
}

export async function POST(request: Request) {
  try {
    const { messages } = await request.json()

    // Define the search tool
    const tools = [
      {
        type: 'function' as const,
        function: {
          name: 'search_web',
          description: 'Search the web for up-to-date information, current events, news, prices, sports scores, or anything after August 2024.',
          parameters: {
            type: 'object',
            properties: {
              query: {
                type: 'string',
                description: 'A clear, concise search query in English.',
              },
            },
            required: ['query'],
          },
        },
      },
    ]

    // First call: Ask the model if it needs to use the tool
    let chatCompletion = await groq.chat.completions.create({
      messages: [SYSTEM_MESSAGE, ...messages],
      model: 'meta-llama/llama-4-scout-17b-16e-instruct',
      temperature: 0.7,
      max_tokens: 1024,
      tools,
      tool_choice: 'auto',
    })

    const message = chatCompletion.choices[0]?.message

    // If the model wants to use the tool
    if (message?.tool_calls?.length) {
      const toolCall = message.tool_calls[0]
      const functionArgs = JSON.parse(toolCall.function.arguments)

      const searchResults = await searchWeb(functionArgs.query)

      // Second call: Provide search results back to the model
      chatCompletion = await groq.chat.completions.create({
        messages: [
          SYSTEM_MESSAGE,
          ...messages,
          message, // Include the assistant's tool call
          {
            role: 'tool',
            tool_call_id: toolCall.id,
            content: searchResults,
          },
        ],
        model: 'meta-llama/llama-4-scout-17b-16e-instruct',
        temperature: 0.7,
        max_tokens: 1024,
      })
    }

    const responseMessage =
      chatCompletion.choices[0]?.message?.content || 'No response generated'

    return NextResponse.json({ message: responseMessage })
  } catch (error: any) {
    console.error('Groq/Tool error:', error)
    return NextResponse.json(
      { error: 'Failed to get response from AI' },
      { status: 500 }
    )
  }
}