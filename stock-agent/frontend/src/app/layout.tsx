import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Script from "next/script";
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
      <head>
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=G-HDH90MLFDM"
          strategy="afterInteractive"
        />
        <Script id="google-analytics" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());

            gtag('config', 'G-HDH90MLFDM');
          `}
        </Script>
      </head>
      <body className={inter.className}>
        {children}
      </body>
    </html>
  );
}
