"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/app/contexts/AuthContext";
import NotificationBell from "@/app/components/NotificationBell";

export default function Header() {
  const { user, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="bg-[#111111] shadow-sm border-b border-[#2a2a2a]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Desktop Navigation */}
          <div className="flex items-center flex-1">
            <Link href="/" className="text-lg sm:text-xl font-bold text-blue-600 whitespace-nowrap">
              US Stock Assistant
            </Link>
            {user && (
              <nav className="hidden md:flex ml-6 lg:ml-10 space-x-2 lg:space-x-4">
                <Link href="/dashboard" className="text-gray-300 hover:text-blue-400 px-2 lg:px-3 py-2 text-sm lg:text-base whitespace-nowrap">
                  Dashboard
                </Link>
                <Link href="/portfolio" className="text-gray-300 hover:text-blue-400 px-2 lg:px-3 py-2 text-sm lg:text-base whitespace-nowrap">
                  Portfolio
                </Link>
                <Link href="/market" className="text-gray-300 hover:text-blue-400 px-2 lg:px-3 py-2 text-sm lg:text-base whitespace-nowrap">
                  Market
                </Link>
                <Link href="/alerts" className="text-gray-300 hover:text-blue-400 px-2 lg:px-3 py-2 text-sm lg:text-base whitespace-nowrap">
                  Alerts
                </Link>
              </nav>
            )}
          </div>

          {/* Desktop Actions */}
          <div className="hidden md:flex items-center space-x-2 lg:space-x-4">
            {user ? (
              <>
                <NotificationBell />
                <span className="text-gray-300 text-sm lg:text-base hidden lg:inline truncate max-w-[150px]">{user.email}</span>
                <button onClick={logout} className="bg-red-500 hover:bg-red-600 text-white px-3 lg:px-4 py-2 rounded text-sm lg:text-base whitespace-nowrap">
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link href="/login" className="text-gray-300 hover:text-blue-400 px-3 py-2 text-sm lg:text-base">
                  Login
                </Link>
                <Link href="/register" className="bg-blue-600 hover:bg-blue-700 text-white px-3 lg:px-4 py-2 rounded text-sm lg:text-base whitespace-nowrap">
                  Register
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="flex md:hidden items-center space-x-2">
            {user && <NotificationBell />}
            <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="p-2 rounded-md text-gray-300 hover:bg-[#2a2a2a] focus:outline-none focus:ring-2 focus:ring-blue-500" aria-label="Toggle menu">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {mobileMenuOpen ? <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /> : <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-[#2a2a2a] py-4 bg-[#111111]">
            {user ? (
              <>
                <nav className="flex flex-col space-y-2 mb-4">
                  <Link href="/dashboard" className="text-gray-300 hover:text-blue-400 hover:bg-[#2a2a2a] px-4 py-3 rounded-md text-base" onClick={() => setMobileMenuOpen(false)}>
                    Dashboard
                  </Link>
                  <Link href="/portfolio" className="text-gray-300 hover:text-blue-400 hover:bg-[#2a2a2a] px-4 py-3 rounded-md text-base" onClick={() => setMobileMenuOpen(false)}>
                    Portfolio
                  </Link>
                  <Link href="/market" className="text-gray-300 hover:text-blue-400 hover:bg-[#2a2a2a] px-4 py-3 rounded-md text-base" onClick={() => setMobileMenuOpen(false)}>
                    Market
                  </Link>
                  <Link href="/alerts" className="text-gray-300 hover:text-blue-400 hover:bg-[#2a2a2a] px-4 py-3 rounded-md text-base" onClick={() => setMobileMenuOpen(false)}>
                    Alerts
                  </Link>
                </nav>
                <div className="border-t border-[#2a2a2a] pt-4 px-4 space-y-3">
                  <div className="text-gray-300 text-sm truncate">{user.email}</div>
                  <button
                    onClick={() => {
                      logout();
                      setMobileMenuOpen(false);
                    }}
                    className="w-full bg-red-500 hover:bg-red-600 text-white px-4 py-3 rounded text-base">
                    Logout
                  </button>
                </div>
              </>
            ) : (
              <div className="flex flex-col space-y-2 px-4">
                <Link href="/login" className="text-center text-gray-300 hover:text-blue-400 hover:bg-[#2a2a2a] px-4 py-3 rounded-md text-base" onClick={() => setMobileMenuOpen(false)}>
                  Login
                </Link>
                <Link href="/register" className="text-center bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded text-base" onClick={() => setMobileMenuOpen(false)}>
                  Register
                </Link>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  );
}
