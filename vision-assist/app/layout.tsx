import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "VisionAssist - Real-time Object Detection",
  description: "AI-powered object detection running entirely in your browser. Assists visually impaired users by identifying nearby objects in real-time using TensorFlow.js.",
  keywords: ["object detection", "AI", "TensorFlow.js", "accessibility", "computer vision", "assistive technology"],
  authors: [{ name: "Maria Lima" }],
  openGraph: {
    title: "VisionAssist - Real-time Object Detection",
    description: "Privacy-first object detection powered by AI, running entirely in your browser",
    type: "website",
  },
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#000000",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-black dark`}
      >
        {children}
      </body>
    </html>
  );
}
