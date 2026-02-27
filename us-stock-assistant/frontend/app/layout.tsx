import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "./contexts/AuthContext";
import QueryProvider from "./providers/QueryProvider";
import { MonitoringProvider } from "./providers/MonitoringProvider";

export const metadata: Metadata = {
  title: "US Stock Assistant",
  description: "AI-powered portfolio management and stock analysis",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col">
        <MonitoringProvider>
          <QueryProvider>
            <AuthProvider>{children}</AuthProvider>
          </QueryProvider>
        </MonitoringProvider>
      </body>
    </html>
  );
}
