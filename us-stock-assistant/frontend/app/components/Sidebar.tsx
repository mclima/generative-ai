"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/app/contexts/AuthContext";
import NotificationBell from "@/app/components/NotificationBell";

interface SidebarProps {
  isOpen: boolean;
  onClose?: () => void;
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const links = [
    { href: "/dashboard", label: "Dashboard" },
    { href: "/portfolio", label: "Portfolio" },
    { href: "/market", label: "Market Overview" },
    { href: "/alerts", label: "Alerts" },
    { href: "/settings", label: "Settings" },
  ];

  const handleLinkClick = () => {
    if (onClose) onClose();
  };

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && <div className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden" onClick={onClose} aria-hidden="true" />}

      {/* Sidebar */}
      <aside className={`${isOpen ? "translate-x-0" : "-translate-x-full"} fixed lg:static lg:translate-x-0 inset-y-0 left-0 z-50 w-64 bg-[#111111] border-r border-[#2a2a2a] transition-transform duration-300 ease-in-out shadow-lg lg:shadow-none flex flex-col`}>

        {/* App title + mobile close */}
        <div className="flex items-center justify-between px-4 py-4 border-b border-[#2a2a2a]">
          <Link href="/dashboard" onClick={handleLinkClick} className="text-lg font-bold text-blue-500 truncate">
            US Stock Assistant
          </Link>
          <button onClick={onClose} className="lg:hidden p-1 rounded-md text-gray-400 hover:bg-[#2a2a2a]" aria-label="Close sidebar">
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Nav links */}
        <nav className="flex-1 mt-3 px-2">
          {links.map((link) => (
            <Link key={link.href} href={link.href} onClick={handleLinkClick} className={`${pathname === link.href ? "bg-blue-900 text-blue-400" : "text-gray-300 hover:bg-[#2a2a2a]"} group flex items-center px-4 py-3 text-sm font-medium rounded-md mb-1 transition-colors duration-150`}>
              <span className="truncate">{link.label}</span>
            </Link>
          ))}
        </nav>

        {/* User info + logout at bottom */}
        {user && (
          <div className="px-4 py-4 border-t border-[#2a2a2a] space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400 truncate max-w-[140px]">{user.email}</span>
              <NotificationBell />
            </div>
            <button
              onClick={logout}
              className="w-full bg-red-600 hover:bg-red-700 text-white text-sm font-medium py-2 rounded-md transition-colors"
            >
              Logout
            </button>
          </div>
        )}
      </aside>
    </>
  );
}
