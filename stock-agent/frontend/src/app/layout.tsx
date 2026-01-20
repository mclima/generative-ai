import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Stock Agent - AI-Powered US Stock Analysis Dashboard",
  description: "Real-time US stock analysis powered by AI agents. Get intelligent insights, charts, and news for your favorite stocks.",
  keywords: ["stocks", "AI", "analysis", "trading", "dashboard", "real-time"],
  authors: [{ name: "Maria Lima" }],
  openGraph: {
    title: "Stock Agent - AI-Powered US Stock Analysis",
    description: "Real-time US stock analysis powered by AI agents",
    type: "website",
  },
  viewport: "width=device-width, initial-scale=1",
  themeColor: "#000000",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  );
}
