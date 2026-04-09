import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';

export async function POST(request: NextRequest) {
  try {
    const { prompt } = await request.json();

    if (!prompt) {
      return NextResponse.json(
        { error: 'Prompt is required' },
        { status: 400 }
      );
    }

    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
      return NextResponse.json(
        { error: 'OpenAI API key is not configured' },
        { status: 500 }
      );
    }

    const openai = new OpenAI({ apiKey });
    
    const response = await openai.images.generate({
      model: 'gpt-image-1',
      prompt: prompt,
      size: '1024x1024',
      n: 1,
    });
    
    const imageUrl = response.data?.[0]?.url;
    const imageB64 = response.data?.[0]?.b64_json;

    if (!imageUrl && !imageB64) {
      return NextResponse.json(
        { error: 'Failed to generate image - no data returned' },
        { status: 500 }
      );
    }

    const finalImageUrl = imageUrl || `data:image/png;base64,${imageB64}`;
    return NextResponse.json({ imageUrl: finalImageUrl });
  } catch (error) {
    if (error instanceof OpenAI.APIError) {
      return NextResponse.json(
        { error: error.message },
        { status: error.status || 500 }
      );
    }

    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'An unexpected error occurred' },
      { status: 500 }
    );
  }
}
