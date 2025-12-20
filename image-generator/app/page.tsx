'use client';

import { useState } from 'react';
import { Sparkles, Download, Loader2, ImageIcon } from 'lucide-react';

const examplePrompts = [
  'A dramatic poster for a mystery series set in Victorian London with fog and gas lamps',
  'A vibrant banner for a comedy show featuring colorful characters in a modern city',
  'An epic fantasy poster with dragons flying over medieval castles at sunset',
  'A sleek promotional image for a tech documentary with holographic displays and data visualization',
];

export default function Home() {
  const [prompt, setPrompt] = useState('');
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateImage = async () => {
    if (!prompt.trim()) return;

    setIsLoading(true);
    setError(null);
    setImageUrl(null);

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate image');
      }

      setImageUrl(data.imageUrl);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleExampleClick = (examplePrompt: string) => {
    setPrompt(examplePrompt);
  };

  const handleDownload = async () => {
    if (!imageUrl) return;

    try {
      const response = await fetch('/api/download', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ imageUrl }),
      });

      if (!response.ok) {
        throw new Error('Download failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `image-${Date.now()}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-black via-gray-900 to-black">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <span className="text-4xl">🎨</span>
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-500 via-pink-500 to-orange-400 bg-clip-text text-transparent">
              AI Image Generator
            </h1>
          </div>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Transform your creative ideas into stunning visual images. 
            Enter a detailed text prompt to generate bespoke images for banners and posters.
          </p>
        </div>

        {/* Main Content - Side by Side */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Side - Prompt Input */}
          <div className="space-y-6">
            {/* Input Section */}
            <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-800">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Enter your image prompt
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey && prompt.trim() && !isLoading) {
                    e.preventDefault();
                    generateImage();
                  }
                }}
                placeholder="Example: A cinematic poster for a sci-fi thriller featuring a futuristic cityscape at night with neon lights"
                className="w-full h-40 px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none transition-all"
              />
              <button
                onClick={generateImage}
                disabled={isLoading || !prompt.trim()}
                className="mt-4 w-full py-4 px-6 bg-gradient-to-r from-purple-600 to-pink-500 hover:from-purple-500 hover:to-pink-400 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all duration-200 flex items-center justify-center gap-2 shadow-lg shadow-purple-500/20"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    Generate Image
                  </>
                )}
              </button>
            </div>

            {/* Example Prompts */}
            <div>
              <h3 className="text-sm font-medium text-gray-400 mb-3">Try an example:</h3>
              <div className="grid grid-cols-1 gap-3">
                {examplePrompts.map((example, index) => (
                  <button
                    key={index}
                    onClick={() => handleExampleClick(example)}
                    className="text-left p-3 bg-gray-800/30 hover:bg-gray-800/50 border border-gray-700/50 hover:border-gray-600 rounded-lg text-sm text-gray-300 transition-all duration-200"
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>

            {/* Error Display */}
            {error && (
              <div className="p-4 bg-red-900/20 border border-red-800 rounded-xl text-red-400">
                {error}
              </div>
            )}
          </div>

          {/* Right Side - Image Display */}
          <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-800 h-fit">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-200">Generated Image</h2>
              {imageUrl && (
                <button
                  onClick={handleDownload}
                  className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm text-gray-300 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  Download
                </button>
              )}
            </div>
            <div className="aspect-square bg-gray-800/50 rounded-xl overflow-hidden flex items-center justify-center">
              {isLoading ? (
                <div className="flex flex-col items-center gap-4 text-gray-500">
                  <Loader2 className="w-12 h-12 animate-spin" />
                  <p>Creating your image...</p>
                </div>
              ) : imageUrl ? (
                <img
                  src={imageUrl}
                  alt="Generated image"
                  className="w-full h-full object-contain"
                />
              ) : (
                <div className="flex flex-col items-center gap-4 text-gray-600">
                  <ImageIcon className="w-16 h-16" />
                  <p>Your generated image will appear here</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-12 text-center text-gray-600 text-sm">
          Powered by OpenAI DALL-E
        </footer>
      </div>
    </main>
  );
}
