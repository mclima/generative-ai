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

    console.log('Attempting to generate image with model: gpt-image-1');
    console.log('Prompt:', prompt);
    
    const response = await openai.images.generate({
      model: 'gpt-image-1',
      prompt: prompt,
      size: '1024x1024',
      n: 1,
    });

    console.log('API Response received');
    
    const imageUrl = response.data?.[0]?.url;
    const imageB64 = response.data?.[0]?.b64_json;

    if (!imageUrl && !imageB64) {
      console.error('No image data in response');
      return NextResponse.json(
        { error: 'Failed to generate image - no data returned' },
        { status: 500 }
      );
    }

    const finalImageUrl = imageUrl || `data:image/png;base64,${imageB64}`;
    return NextResponse.json({ imageUrl: finalImageUrl });
  } catch (error) {
    console.error('Error generating image:', error);
    console.error('Error details:', JSON.stringify(error, null, 2));
    
    if (error instanceof OpenAI.APIError) {
      console.error('OpenAI API Error:', {
        message: error.message,
        status: error.status,
        code: error.code,
        type: error.type
      });
      return NextResponse.json(
        { error: `OpenAI Error: ${error.message} (Code: ${error.code}, Status: ${error.status})` },
        { status: error.status || 500 }
      );
    }

    return NextResponse.json(
      { error: `Error: ${error instanceof Error ? error.message : 'An unexpected error occurred'}` },
      { status: 500 }
    );
  }
}
