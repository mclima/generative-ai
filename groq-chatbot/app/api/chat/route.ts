import Groq from 'groq-sdk'
import { NextResponse } from 'next/server'

const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY,
})

export async function POST(request: Request) {
  try {
    const { messages } = await request.json()

    const chatCompletion = await groq.chat.completions.create({
      messages: [
        {
          role: 'system',
          content: 'You are a helpful, friendly AI assistant. Provide clear, concise, and accurate responses. Be conversational but professional.',
        },
        ...messages,
      ],
      model: 'llama-3.3-70b-versatile',
      temperature: 0.7,
      max_tokens: 1024,
    })

    const responseMessage = chatCompletion.choices[0]?.message?.content || 'No response generated'

    return NextResponse.json({ message: responseMessage })
  } catch (error) {
    console.error('Groq API error:', error)
    return NextResponse.json(
      { error: 'Failed to get response from AI' },
      { status: 500 }
    )
  }
}
