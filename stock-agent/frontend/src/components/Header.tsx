"use client";

import { TrendingUp } from "lucide-react";

export default function Header() {
  return (
    <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-lg">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Stock Agent</h1>
              <p className="text-xs text-gray-400">AI-Powered Analysis</p>
            </div>
          </div>
          <div className="hidden md:flex items-center space-x-4">
            <div className="text-sm text-gray-400">
              <span className="text-green-400">●</span> Free Tier
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
