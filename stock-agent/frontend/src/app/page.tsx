"use client";

import { useState, useEffect } from "react";
import StockSearch from "@/components/StockSearch";
import StockDashboard from "@/components/StockDashboard";
import InfoBanner from "@/components/InfoBanner";
import RateLimitAlert from "@/components/RateLimitAlert";

export default function Home() {
  const [selectedSymbol, setSelectedSymbol] = useState<string>("");
  const [showAlert, setShowAlert] = useState(false);

  useEffect(() => {
    // Show alert when page loads
    setShowAlert(true);
  }, []);

  return (
    <div className="min-h-screen">
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 bg-clip-text text-transparent">
            AI-Powered US Stock Analysis
          </h1>
          <p className="text-gray-400 text-lg">
            Get real-time insights, charts, and AI-driven analysis for any stock
          </p>
        </div>

        <RateLimitAlert show={showAlert} onClose={() => setShowAlert(false)} />
        <InfoBanner />
        <StockSearch onSymbolSelect={setSelectedSymbol} />

        {selectedSymbol && (
          <div className="mt-8">
            <StockDashboard symbol={selectedSymbol} />
          </div>
        )}

        {!selectedSymbol && (
          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="card card-hover">
              <div className="text-blue-500 mb-4">
                <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Real-Time Charts</h3>
              <p className="text-gray-400">
                Interactive charts with historical data and technical indicators
              </p>
            </div>

            <div className="card card-hover">
              <div className="text-purple-500 mb-4">
                <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">AI Insights</h3>
              <p className="text-gray-400">
                Powered by OpenAI to provide intelligent stock analysis and recommendations
              </p>
            </div>

            <div className="card card-hover">
              <div className="text-pink-500 mb-4">
                <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Latest News</h3>
              <p className="text-gray-400">
                Stay updated with the latest news and market sentiment analysis
              </p>
            </div>
          </div>
        )}

        <div className="max-w-3xl mx-auto mt-12 pt-4 border-t border-gray-800">
          <p className="text-sm text-gray-400 text-center flex items-center justify-center gap-2">
            © {new Date().getFullYear()} maria c. lima
            <span>|</span>
            <a 
              href="mailto:maria.lima.hub@gmail.com"
              className="hover:text-white transition-colors flex items-center gap-1"
              aria-label="Email maria.lima.hub@gmail.com"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
              </svg>
              <span>maria.lima.hub@gmail.com</span>
            </a>
          </p>
        </div>
      </main>
    </div>
  );
}
