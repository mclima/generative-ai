// app/api/chat/route.ts 
import Groq from 'groq-sdk'
import { NextResponse } from 'next/server'

const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY,
})

async function fetchPageContent(url: string): Promise<string> {
  try {
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
      },
      signal: AbortSignal.timeout(5000),
    })
    
    if (!response.ok) return ''
    
    const html = await response.text()
    const textContent = html
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, '')
      .replace(/<[^>]+>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
    
    return textContent.slice(0, 3000)
  } catch (error) {
    return ''
  }
}

async function searchWeb(query: string): Promise<string> {
  if (!process.env.SERPER_API_KEY) {
    console.error('SERPER_API_KEY is not configured')
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

    if (!response.ok) {
      const errorText = await response.text()
      console.error('Serper API error:', response.status, errorText)
      throw new Error(`Search failed with status ${response.status}`)
    }

    const data = await response.json()

    if (!data.organic || data.organic.length === 0) {
      return 'No search results found for this query.'
    }

    let results = ''
    
    // Include answer box if available (Google's featured snippet with direct answers)
    if (data.answerBox) {
      results += `**Featured Answer:**\n${data.answerBox.answer || data.answerBox.snippet || ''}\n\n`
    }

    // Include knowledge graph data if available (for entities like stocks, people, places)
    if (data.knowledgeGraph) {
      results += `**Quick Facts:**\n`
      if (data.knowledgeGraph.title) results += `${data.knowledgeGraph.title}\n`
      if (data.knowledgeGraph.description) results += `${data.knowledgeGraph.description}\n`
      if (data.knowledgeGraph.attributes) {
        Object.entries(data.knowledgeGraph.attributes).forEach(([key, value]) => {
          results += `${key}: ${value}\n`
        })
      }
      results += '\n'
    }

    // Format comprehensive search results with all available data
    results += data.organic
      .slice(0, 5)
      .map((result: any, i: number) => {
        let entry = `${i + 1}. **${result.title}**\n${result.snippet}`
        
        // Include additional rich data if available
        if (result.date) entry += `\nDate: ${result.date}`
        if (result.price) entry += `\nPrice: ${result.price}`
        if (result.rating) entry += `\nRating: ${result.rating}`
        
        entry += `\nSource: ${result.link}`
        return entry
      })
      .join('\n\n')

    return results
  } catch (error) {
    console.error('Serper search error:', error)
    return 'Search failed. Please try again or rephrase your question.'
  }
}

const SYSTEM_MESSAGE = {
  role: 'system' as const,
  content: 'You are a helpful, friendly AI assistant with a knowledge cutoff of August 2024. IMPORTANT: When users ask about current events, news, dates, weather, prices, sports, or anything time-sensitive, you MUST use the search_web tool to get accurate, up-to-date information. Do not guess or use outdated information. If unsure whether something has changed since August 2024, use search_web to verify.',
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
          description: 'REQUIRED for current/recent information: Search the web for real-time data including current events, today\'s date, news, weather, prices, sports scores, political updates, or ANY information that may have changed since August 2024. Use this tool whenever accuracy requires up-to-date information.',
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