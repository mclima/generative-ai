"use client";

import { useState } from "react";
import Sidebar from "@/app/components/Sidebar";
import Footer from "@/app/components/Footer";
import { ProtectedRoute } from "@/app/components/ProtectedRoute";
import { NotificationProvider } from "@/app/contexts/NotificationContext";
import { PreferencesProvider } from "@/app/contexts/PreferencesContext";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <ProtectedRoute>
      <PreferencesProvider>
        <NotificationProvider>
          <div className="min-h-screen flex bg-[#0a0a0a] text-white">
            <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
            <div className="flex-1 flex flex-col overflow-hidden">
              {/* Mobile top bar — always visible on small screens */}
              <div className="lg:hidden sticky top-0 z-30 bg-[#111111] border-b border-[#2a2a2a] px-4 py-3 flex items-center justify-between">
                <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 rounded-md text-gray-300 hover:bg-[#2a2a2a] focus:outline-none focus:ring-2 focus:ring-blue-500" aria-label="Toggle sidebar">
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </button>
                <span className="text-base font-bold text-blue-500">US Stock Assistant</span>
                <div className="w-10" />
              </div>
              <main className="flex-1 overflow-y-auto bg-[#0a0a0a]">
                <div className="p-4 sm:p-6 lg:p-8">{children}</div>
              </main>
              <Footer />
            </div>
          </div>
        </NotificationProvider>
      </PreferencesProvider>
    </ProtectedRoute>
  );
}
