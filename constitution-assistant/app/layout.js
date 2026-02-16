import './globals.css'
import Script from 'next/script'

export const metadata = {
  title: 'Constitution Assistant',
  description: 'AI-powered chatbot for constitution inquiries',
}

export default function RootLayout({ children }) {
  return (
     <html lang="en">
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
      <body>{children}</body>
    </html>
  )
}
